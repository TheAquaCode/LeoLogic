"""
API Routes for File Organizer
"""

import os
import json
import time
import shutil
from pathlib import Path
from flask import request, jsonify
from config.settings import CONFIG_FILE
from .state import state
from .file_watcher import start_watching, stop_watching
from .file_processor import process_file


def load_config():
    """Load watched folders and categories from disk"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            state.watched_folders = config.get("watched_folders", [])
            state.categories = config.get("categories", [])
            print(f"📂 Loaded {len(state.watched_folders)} watched folders")
            print(f"🏷️  Loaded {len(state.categories)} categories")


def save_config():
    """Save watched folders and categories"""
    config = {
        "watched_folders": state.watched_folders,
        "categories": state.categories
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def register_routes(app):
    """Register all API routes"""
    
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "online",
            "initialized": state.is_initialized
        })

    # Watched Folders
    @app.route("/api/watched-folders", methods=["GET"])
    def get_folders():
        return jsonify(state.watched_folders)

    @app.route("/api/watched-folders", methods=["POST"])
    def add_folder():
        data = request.json
        folder = {
            "id": int(time.time() * 1000),
            "name": data.get("name"),
            "path": data.get("path"),
            "status": "Active",
            "files": 0,
            "lastActivity": "Just now"
        }
        state.watched_folders.append(folder)
        save_config()
        start_watching(folder["id"], folder["path"])
        return jsonify(folder)

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
            return jsonify(folder)
        return jsonify({"error": "Folder not found"}), 404

    @app.route("/api/watched-folders/<int:folder_id>", methods=["DELETE"])
    def delete_folder(folder_id):
        folder = next((f for f in state.watched_folders if f["id"] == folder_id), None)
        if folder:
            stop_watching(folder_id)
            state.watched_folders = [f for f in state.watched_folders if f["id"] != folder_id]
            save_config()
            return jsonify({"status": "success", "message": "Folder deleted"})
        return jsonify({"error": "Folder not found"}), 404

    # Categories
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
            "fileTypes": [],
            "rules": 0,
            "color": "bg-blue-500"
        }
        state.categories.append(category)
        save_config()
        return jsonify(category)

    @app.route("/api/categories/<int:category_id>", methods=["DELETE"])
    def delete_category(category_id):
        category = next((c for c in state.categories if c["id"] == category_id), None)
        if category:
            state.categories = [c for c in state.categories if c["id"] != category_id]
            save_config()
            return jsonify({"status": "success", "message": "Category deleted"})
        return jsonify({"error": "Category not found"}), 404

    @app.route("/api/categories/<int:category_id>", methods=["PATCH"])
    def update_category(category_id):
        category = next((c for c in state.categories if c["id"] == category_id), None)
        if category:
            data = request.json
            if "path" in data:
                category["path"] = data["path"]
            if "name" in data:
                category["name"] = data["name"]
            save_config()
            return jsonify(category)
        return jsonify({"error": "Category not found"}), 404

    # Manual folder processing
    @app.route("/api/process-folder/<int:folder_id>", methods=["POST"])
    def process_folder_route(folder_id):
        folder = next((f for f in state.watched_folders if f["id"] == folder_id), None)
        if not folder or not Path(folder["path"]).exists():
            return jsonify({"error": "Folder not found"}), 404
        results = []
        for file_path in Path(folder["path"]).glob("*"):
            if file_path.is_file():
                results.append(process_file(str(file_path), folder_id))
        return jsonify({"processed": len(results), "results": results})
    
    # Upload and process endpoint
    @app.route("/api/upload-and-process", methods=["POST"])
    def upload_and_process():
        """Handle file upload and process without adding as watched folder"""
        try:
            if 'file' not in request.files:
                return jsonify({"error": "No file provided"}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            # Create temporary directory for uploads
            from config.settings import DATA_DIR
            upload_dir = DATA_DIR / "uploads"
            upload_dir.mkdir(exist_ok=True)
            
            # Save file temporarily
            temp_path = upload_dir / file.filename
            file.save(str(temp_path))
            
            # Process the file (using -1 as folder_id to indicate upload)
            result = process_file(str(temp_path), -1)
            
            return jsonify(result)
            
        except Exception as e:
            print(f"❌ Error in upload-and-process: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500
    
    # History endpoints
    @app.route("/api/history", methods=["GET"])
    def get_history():
        """Get file movement history"""
        try:
            from .file_history import file_history
            limit = request.args.get('limit', 100, type=int)
            history = file_history.get_history(limit)
            return jsonify(history)
        except Exception as e:
            print(f"❌ Error getting history: {e}")
            import traceback
            traceback.print_exc()
            return jsonify([])  # Return empty array on error
    
    @app.route("/api/history/stats", methods=["GET"])
    def get_history_stats():
        """Get history statistics"""
        try:
            from .file_history import file_history
            stats = file_history.get_stats()
            return jsonify(stats)
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "total": 0,
                "completed": 0,
                "undone": 0,
                "pending": 0,
                "success_rate": "0%"
            })
    
    @app.route("/api/history/<int:movement_id>/undo", methods=["POST"])
    def undo_movement(movement_id):
        """Undo a file movement"""
        try:
            from .file_history import file_history
            
            movement = file_history.get_movement_by_id(movement_id)
            if not movement:
                return jsonify({"error": "Movement not found"}), 404
            
            if movement.get('status') == 'undone':
                return jsonify({"error": "Already undone"}), 400
            
            to_path = Path(movement['toPath'])
            from_path = Path(movement['fromPath'])
            
            # Check if destination file still exists
            if not to_path.exists():
                return jsonify({"error": "File no longer exists at destination"}), 404
            
            # Move back to original location
            shutil.move(str(to_path), str(from_path))
            
            # Update status
            file_history.update_movement_status(movement_id, 'undone')
            
            print(f"↩️ Undone: {to_path} -> {from_path}")
            
            return jsonify({
                "status": "success",
                "message": "File movement undone",
                "movement": file_history.get_movement_by_id(movement_id)
            })
        except Exception as e:
            print(f"❌ Error undoing movement: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/history/<int:movement_id>/open", methods=["POST"])
    def open_file_location(movement_id):
        """Get the file location for opening in system explorer"""
        try:
            from .file_history import file_history
            
            movement = file_history.get_movement_by_id(movement_id)
            if not movement:
                return jsonify({"error": "Movement not found"}), 404
            
            # Return the directory path
            file_path = Path(movement['toPath'])
            directory = str(file_path.parent)
            
            return jsonify({
                "directory": directory,
                "filename": movement['filename']
            })
        except Exception as e:
            print(f"❌ Error opening file location: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500