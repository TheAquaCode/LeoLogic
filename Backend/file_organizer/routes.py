import os
import json
import time
from datetime import datetime
from pathlib import Path
from flask import request, jsonify
from config.settings import CONFIG_FILE, DATA_DIR
from .state import state
from .file_watcher import start_watching, stop_watching
from .file_processor import process_file
from .bulk_processor import bulk_processor
from .rag_generator import RAGGenerator
from .file_counter import count_files_in_folder

# History storage
HISTORY_FILE = DATA_DIR / "file_history.json"

def load_history():
    """Load file movement history"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_history(history):
    """Save file movement history"""
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def add_to_history(movement):
    """Add a movement to history"""
    history = load_history()
    movement['id'] = int(time.time() * 1000)
    movement['timestamp'] = time.time()
    history.insert(0, movement)
    
    if len(history) > 1000:
        history = history[:1000]
    
    save_history(history)
    return movement

def format_time_ago(timestamp):
    """Format timestamp as relative time"""
    now = time.time()
    diff = now - timestamp
    
    if diff < 60:
        return "Just now"
    elif diff < 3600:
        mins = int(diff / 60)
        return f"{mins} minute{'s' if mins != 1 else ''} ago"
    elif diff < 86400:
        hours = int(diff / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = int(diff / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"

def load_config():
    """Load watched folders and categories from disk"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            state.watched_folders = config.get("watched_folders", [])
            state.categories = config.get("categories", [])
            state.auto_organize = config.get("auto_organize", False)
            print(f"📂 Loaded {len(state.watched_folders)} watched folders")
            print(f"🏷️ Loaded {len(state.categories)} categories")
            print(f"⚡ Auto-organize: {'ON' if state.auto_organize else 'OFF'}")

def save_config():
    """Save watched folders and categories"""
    config = {
        "watched_folders": state.watched_folders,
        "categories": state.categories,
        "auto_organize": state.auto_organize
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def register_routes(app):
    """Register all API routes"""

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "online",
            "initialized": state.is_initialized,
            "stats": state.processing_stats,
        })

    # ==================== SETTINGS ====================
    
    @app.route("/api/settings/auto-organize", methods=["GET"])
    def get_auto_organize():
        """Get auto-organize setting"""
        return jsonify({"enabled": state.auto_organize})
    
    @app.route("/api/settings/auto-organize", methods=["POST"])
    def set_auto_organize():
        """Set auto-organize setting"""
        data = request.json
        state.auto_organize = data.get("enabled", False)
        save_config()
        print(f"⚡ Auto-organize: {'ON' if state.auto_organize else 'OFF'}")
        return jsonify({"enabled": state.auto_organize})

    # ==================== HISTORY ====================
    
    @app.route("/api/history", methods=["GET"])
    def get_history():
        """Get file movement history"""
        try:
            limit = int(request.args.get('limit', 100))
            history = load_history()
            
            formatted_history = []
            for item in history[:limit]:
                formatted_history.append({
                    'id': item.get('id'),
                    'filename': item.get('filename', 'Unknown'),
                    'fromPath': item.get('from_path', ''),
                    'toPath': item.get('to_path', ''),
                    'category': item.get('category', 'Unknown'),
                    'confidence': item.get('confidence', '0%'),
                    'detection': item.get('detection', 'AI Classification'),
                    'status': item.get('status', 'completed'),
                    'timestamp': item.get('timestamp', time.time()),
                    'timeAgo': format_time_ago(item.get('timestamp', time.time()))
                })
            
            return jsonify(formatted_history)
        except Exception as e:
            print(f"Error loading history: {e}")
            return jsonify([])
    
    @app.route("/api/history/stats", methods=["GET"])
    def get_history_stats():
        """Get history statistics"""
        try:
            history = load_history()
            
            completed = sum(1 for h in history if h.get('status') == 'completed')
            undone = sum(1 for h in history if h.get('status') == 'undone')
            total = len(history)
            
            success_rate = f"{int((completed / total * 100) if total > 0 else 0)}%"
            
            return jsonify({
                'total': total,
                'completed': completed,
                'undone': undone,
                'pending': 0,
                'success_rate': success_rate
            })
        except Exception as e:
            print(f"Error loading history stats: {e}")
            return jsonify({
                'total': 0,
                'completed': 0,
                'undone': 0,
                'pending': 0,
                'success_rate': '0%'
            })
    
    @app.route("/api/history/<int:movement_id>/undo", methods=["POST"])
    def undo_movement(movement_id):
        """Undo a file movement"""
        try:
            history = load_history()
            movement = next((h for h in history if h.get('id') == movement_id), None)
            
            if not movement:
                return jsonify({'error': 'Movement not found'}), 404
            
            if movement.get('status') == 'undone':
                return jsonify({'error': 'Already undone'}), 400
            
            from_path = Path(movement['to_path'])
            to_path = Path(movement['from_path'])
            
            if from_path.exists():
                to_path.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.move(str(from_path), str(to_path))
                
                movement['status'] = 'undone'
                save_history(history)
                
                return jsonify({'success': True, 'message': 'File moved back'})
            else:
                return jsonify({'error': 'File not found at destination'}), 404
                
        except Exception as e:
            print(f"Error undoing movement: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route("/api/history/<int:movement_id>/open", methods=["POST"])
    def open_file_location(movement_id):
        """Get file location for opening"""
        try:
            history = load_history()
            movement = next((h for h in history if h.get('id') == movement_id), None)
            
            if not movement:
                return jsonify({'error': 'Movement not found'}), 404
            
            file_path = Path(movement['to_path'])
            directory = str(file_path.parent)
            
            return jsonify({'directory': directory})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # ==================== WATCHED FOLDERS ====================
    
    @app.route("/api/watched-folders", methods=["GET"])
    def get_folders():
        folders = []
        for folder in state.watched_folders:
            folder_data = folder.copy()
            file_count = count_files_in_folder(folder['path'])
            print(f"Folder {folder['name']}: counted {file_count} files")  # Debug log
            folder_data['fileCount'] = file_count
            folders.append(folder_data)
        return jsonify(folders)

    @app.route("/api/watched-folders", methods=["POST"])
    def add_folder():
        data = request.json
        folder_path = data.get("path")
        folder = {
            "id": int(time.time() * 1000),
            "name": data.get("name"),
            "path": folder_path,
            "status": "Active",
            "fileCount": count_files_in_folder(folder_path)
        }
        state.watched_folders.append(folder)
        save_config()
        start_watching(folder["id"], folder["path"])
        return jsonify({"folder": folder})

    @app.route("/api/watched-folders/<int:folder_id>/toggle", methods=["POST"])
    def toggle_folder(folder_id):
        folder = next((f for f in state.watched_folders if f["id"] == folder_id), None)
        if folder:
            folder["status"] = "Paused" if folder["status"] == "Active" else "Active"
            if folder["status"] == "Active":
                start_watching(folder["id"], folder["path"])
            else:
                stop_watching(folder["id"])
            save_config()
            return jsonify({"folder": folder})
        return jsonify({"error": "Folder not found"}), 404

    @app.route("/api/watched-folders/<int:folder_id>", methods=["DELETE"])
    def delete_folder(folder_id):
        folder = next((f for f in state.watched_folders if f["id"] == folder_id), None)
        if folder:
            stop_watching(folder_id)
            state.watched_folders = [
                f for f in state.watched_folders if f["id"] != folder_id
            ]
            save_config()
            return jsonify({"message": "Folder deleted successfully"})
        return jsonify({"error": "Folder not found"}), 404

    # ==================== CATEGORIES ====================
    
    @app.route("/api/categories", methods=["GET"])
    def get_categories():
        return jsonify(state.categories)

    @app.route("/api/categories", methods=["POST"])
    def add_category():
        data = request.json
        category = {
            "id": int(time.time() * 1000),
            "name": data.get("name"),
            "path": data.get("path"),
        }
        state.categories.append(category)
        save_config()
        return jsonify({"category": category})

    @app.route("/api/categories/<int:category_id>", methods=["PUT"])
    def update_category(category_id):
        category = next((c for c in state.categories if c["id"] == category_id), None)
        if category:
            data = request.json
            if "name" in data:
                category["name"] = data["name"]
            if "path" in data:
                category["path"] = data["path"]
            save_config()
            return jsonify({"category": category})
        return jsonify({"error": "Category not found"}), 404

    @app.route("/api/categories/<int:category_id>", methods=["DELETE"])
    def delete_category(category_id):
        category = next((c for c in state.categories if c["id"] == category_id), None)
        if category:
            state.categories = [c for c in state.categories if c["id"] != category_id]
            save_config()
            return jsonify({"message": "Category deleted successfully"})
        return jsonify({"error": "Category not found"}), 404

    # ==================== FILE PROCESSING ====================
    
    @app.route("/api/process-folder/<int:folder_id>", methods=["POST"])
    def process_folder_route(folder_id):
        folder = next((f for f in state.watched_folders if f["id"] == folder_id), None)
        if not folder or not Path(folder["path"]).exists():
            return jsonify({"error": "Folder not found"}), 404
        
        results = []
        for file_path in Path(folder["path"]).glob("*"):
            if file_path.is_file():
                result = process_file(str(file_path), folder_id)
                results.append(result)
                
                if result.get('status') == 'success':
                    add_to_history({
                        'filename': result['file_name'],
                        'from_path': str(file_path),
                        'to_path': result.get('destination', str(file_path)),
                        'category': result.get('category', 'Unknown'),
                        'confidence': f"{int(result.get('confidence', 0) * 100)}%",
                        'detection': 'AI Classification',
                        'status': 'completed'
                    })
        
        # Get updated file count after processing
        updated_file_count = count_files_in_folder(folder["path"])
        
        return jsonify({
            "processed": len(results), 
            "results": results,
            "fileCount": updated_file_count
        })

    @app.route("/api/upload-and-process", methods=["POST"])
    def upload_and_process():
        """Upload and process a single file"""
        from werkzeug.utils import secure_filename

        try:
            if "file" not in request.files:
                return jsonify({"status": "error", "error": "No file provided"}), 400

            file = request.files["file"]
            if not file.filename:
                return jsonify({"status": "error", "error": "No file selected"}), 400

            temp_dir = Path(DATA_DIR) / "temp_uploads"
            temp_dir.mkdir(parents=True, exist_ok=True)

            filename = secure_filename(file.filename)
            file_path = temp_dir / filename

            counter = 1
            while file_path.exists():
                name_part = Path(filename).stem
                ext_part = Path(filename).suffix
                file_path = temp_dir / f"{name_part}_{counter}{ext_part}"
                counter += 1

            file.save(str(file_path))

            result = process_file(str(file_path), folder_id=0)
            
            if result.get('status') == 'success':
                add_to_history({
                    'filename': result['file_name'],
                    'from_path': str(file_path),
                    'to_path': result.get('destination', str(file_path)),
                    'category': result.get('category', 'Unknown'),
                    'confidence': f"{int(result.get('confidence', 0) * 100)}%",
                    'detection': 'AI Classification',
                    'status': 'completed'
                })

            return jsonify(result)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"status": "error", "error": str(e)}), 500

    # ==================== RAG & STATS ====================
    
    @app.route("/api/rag/search", methods=["POST"])
    def search_rag():
        query = request.json.get("query", "")
        max_results = request.json.get("max_results", 5)

        if not query:
            return jsonify({"error": "Query required"}), 400

        results = RAGGenerator.search_rag(query, max_results)
        return jsonify({"results": results})

    @app.route("/api/stats", methods=["GET"])
    def get_stats():
        return jsonify(state.processing_stats)