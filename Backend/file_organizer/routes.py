"""
API Routes for File Organizer
Includes history tracking and settings endpoints
"""

import json
import os
import threading
import stat
import shutil
from pathlib import Path
from flask import request, jsonify
from datetime import datetime
from config.settings import CONFIG_FILE, DATA_DIR, load_user_settings, save_user_settings
from .state import state, CACHE_FILE
from .file_watcher import start_watching, stop_watching, start_all_watchers
from .file_processor import process_file
from .rag_generator import RAGGenerator
from .file_counter import count_files_in_folder
from utils.logger import update_log_level, setup_logger
from config import settings as cfg

logger = setup_logger(__name__)

HISTORY_FILE = DATA_DIR / "file_history.json"
RAG_DATA_DIR = DATA_DIR / "rag_data"
TEMP_UPLOADS_DIR = DATA_DIR / "temp_uploads"

# ... (Previous helper functions load_config, save_config, etc. stay same) ...

def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                state.watched_folders = config.get('watched_folders', [])
                for f in state.watched_folders:
                    if 'last_activity_timestamp' not in f:
                        f['last_activity_timestamp'] = 0
                state.categories = config.get('categories', [])
                state.auto_organize = config.get('auto_organize', False)
        except Exception: pass

def save_config():
    try:
        config = {
            'watched_folders': state.watched_folders,
            'categories': state.categories,
            'auto_organize': state.auto_organize
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception: pass

def load_history():
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception: return []

def save_history(history):
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception: pass

def calculate_time_ago(timestamp):
    try:
        if not timestamp or timestamp == 0: return "Never"
        now = datetime.now().timestamp()
        diff = now - timestamp
        if diff < 60: return "Just now"
        elif diff < 3600: return f"{int(diff / 60)}m ago"
        elif diff < 86400: return f"{int(diff / 3600)}h ago"
        else: return f"{int(diff / 86400)}d ago"
    except: return "Never"

def is_hidden_check(path):
    if path.name.startswith('.'): return True
    if os.name == 'nt':
        try:
            attrs = path.stat().st_file_attributes
            if attrs & stat.FILE_ATTRIBUTE_HIDDEN: return True
        except: pass
    return False

def register_routes(app):
    # ... (health check, settings get/post, etc) ...
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'online', 'models_ready': state.is_initialized, 'watched_folders': len(state.watched_folders), 'categories': len(state.categories)})

    @app.route('/api/settings', methods=['GET'])
    def get_settings():
        settings = load_user_settings()
        if not settings:
            settings = {'baseTheme': 'light', 'accentColor': 'blue', 'confidenceThresholds': {'text': 85, 'images': 80, 'audio': 75, 'video': 70}, 'fallbackBehavior': 'Skip file', 'preloadModels': True, 'modelToggles': {'textClassification': True, 'imageRecognition': True, 'audioProcessing': True, 'videoAnalysis': True}, 'scanFrequency': 'Hourly', 'runOnStartup': False, 'desktopNotifications': True, 'minimizeToTray': True, 'maxFileSize': 500, 'skipHiddenFiles': True, 'preserveMetadata': True, 'createBackups': False, 'logLevel': 'Info'}
        return jsonify(settings)

    @app.route('/api/settings', methods=['POST'])
    def update_settings():
        settings = request.json
        success = save_user_settings(settings)
        start_all_watchers()
        if 'logLevel' in settings: update_log_level(settings['logLevel'])
        return jsonify({'success': True, 'settings': settings}) if success else (jsonify({'error': 'Failed'}), 500)

    # --- NEW CLEAR CACHE ENDPOINT ---
    @app.route('/api/settings/clear-cache', methods=['POST'])
    def clear_cache():
        try:
            counts = {'rag': 0, 'temp': 0, 'cache': 0}
            
            # 1. Clear RAG Data
            if RAG_DATA_DIR.exists():
                for f in RAG_DATA_DIR.iterdir():
                    if f.is_file() and f.suffix == '.json':
                        try: 
                            f.unlink()
                            counts['rag'] += 1
                        except: pass

            # 2. Clear Temp Uploads
            if TEMP_UPLOADS_DIR.exists():
                for f in TEMP_UPLOADS_DIR.iterdir():
                    try:
                        if f.is_file(): f.unlink()
                        elif f.is_dir(): shutil.rmtree(f)
                        counts['temp'] += 1
                    except: pass

            # 3. Clear Scanner Cache File
            if CACHE_FILE.exists():
                try:
                    CACHE_FILE.unlink()
                    counts['cache'] += 1
                except: pass
            
            # Reset in-memory cache state
            state.processed_cache = {}
            
            logger.info(f"Cache cleared: {counts}")
            return jsonify({'success': True, 'details': counts})
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/settings/auto-organize', methods=['GET', 'POST'])
    def handle_auto_organize():
        if request.method == 'POST':
            state.auto_organize = request.json.get('enabled', False)
            save_config()
            start_all_watchers()
        return jsonify({'enabled': state.auto_organize})

    @app.route('/api/watched-folders', methods=['GET', 'POST'])
    def handle_watched_folders():
        if request.method == 'POST':
            data = request.json
            new_folder = {'id': len(state.watched_folders) + 1, 'name': data['name'], 'path': data['path'], 'status': 'Active', 'fileCount': count_files_in_folder(data['path']), 'lastActivity': 'Never', 'last_activity_timestamp': 0}
            state.watched_folders.append(new_folder)
            save_config()
            start_all_watchers()
            return jsonify({'folder': new_folder})
        for folder in state.watched_folders:
            folder['fileCount'] = count_files_in_folder(folder['path'])
            ts = folder.get('last_activity_timestamp', 0)
            folder['lastActivity'] = calculate_time_ago(ts)
        save_config()
        return jsonify(state.watched_folders)

    @app.route('/api/watched-folders/<int:folder_id>/toggle', methods=['POST'])
    def toggle_folder(folder_id):
        folder = next((f for f in state.watched_folders if f['id'] == folder_id), None)
        if not folder: return jsonify({'error': 'Not found'}), 404
        folder['status'] = 'Paused' if folder['status'] == 'Active' else 'Active'
        save_config()
        start_all_watchers()
        return jsonify({'folder': folder})

    @app.route('/api/watched-folders/<int:folder_id>', methods=['DELETE'])
    def delete_folder(folder_id):
        stop_watching(folder_id)
        state.watched_folders = [f for f in state.watched_folders if f['id'] != folder_id]
        save_config()
        return jsonify({'success': True})

    @app.route('/api/categories', methods=['GET', 'POST'])
    def handle_categories():
        if request.method == 'POST':
            data = request.json
            new_category = {'id': len(state.categories) + 1, 'name': data['name'], 'path': data['path'], 'color': 'bg-blue-500', 'rules': 0}
            state.categories.append(new_category)
            save_config()
            return jsonify({'category': new_category})
        return jsonify(state.categories)

    @app.route('/api/categories/<int:category_id>', methods=['PUT', 'DELETE'])
    def modify_category(category_id):
        if request.method == 'DELETE':
            state.categories = [c for c in state.categories if c['id'] != category_id]
            save_config()
            return jsonify({'success': True})
        data = request.json
        category = next((c for c in state.categories if c['id'] == category_id), None)
        if not category: return jsonify({'error': 'Not found'}), 404
        if 'name' in data: category['name'] = data['name']
        if 'path' in data: category['path'] = data['path']
        save_config()
        return jsonify({'category': category})

    @app.route('/api/process-folder/<int:folder_id>', methods=['POST'])
    def process_folder_route(folder_id):
        folder = next((f for f in state.watched_folders if f['id'] == folder_id), None)
        if not folder: return jsonify({'error': 'Not found'}), 404
        
        folder_path = Path(folder['path'])
        if not folder_path.exists(): return jsonify({'error': 'Path does not exist'}), 404
        
        settings = load_user_settings() or {}
        skip_hidden = settings.get('skipHiddenFiles', True)

        files = []
        for f in folder_path.iterdir():
            if f.is_file():
                if skip_hidden and is_hidden_check(f): continue
                files.append(str(f))

        state.processing_progress[folder_id] = {'total': len(files), 'completed': 0, 'failed': 0, 'in_progress': 0}
        
        def process_in_background():
            for file_path in files:
                try:
                    result = process_file(file_path, folder_id)
                    if result.get('status') == 'success':
                        state.processing_progress[folder_id]['completed'] += 1
                    else:
                        state.processing_progress[folder_id]['failed'] += 1
                except:
                    state.processing_progress[folder_id]['failed'] += 1
            folder['fileCount'] = count_files_in_folder(folder['path'])
            save_config()
        
        thread = threading.Thread(target=process_in_background, daemon=True)
        thread.start()
        return jsonify({'status': 'accepted', 'total': len(files)})

    @app.route('/api/process-folder/<int:folder_id>/progress', methods=['GET'])
    def get_progress(folder_id):
        return jsonify(state.processing_progress.get(folder_id, {'total': 0, 'completed': 0, 'failed': 0, 'in_progress': 0}))

    @app.route('/api/upload-and-process', methods=['POST'])
    def upload_and_process():
        if request.is_json:
            data = request.json
            file_path = data.get('filePath')
            if file_path:
                try:
                    result = process_file(file_path, folder_id=0)
                    return jsonify(result)
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
        return jsonify({'error': 'Invalid request'}), 400

    @app.route('/api/rag/search', methods=['POST'])
    def search_rag():
        data = request.json
        return jsonify({'results': RAGGenerator.search_rag(data.get('query', ''), data.get('max_results', 5))})

    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        return jsonify(state.processing_stats)

    @app.route('/api/history', methods=['GET'])
    def get_history_route():
        history = load_history()
        for entry in history: entry['timeAgo'] = calculate_time_ago(entry.get('timestamp', 0))
        history.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        return jsonify(history[:request.args.get('limit', 100, type=int)])

    @app.route('/api/history/stats', methods=['GET'])
    def get_history_stats_route():
        history = load_history()
        total = len(history)
        completed = len([h for h in history if h.get('status') == 'completed'])
        undone = len([h for h in history if h.get('status') == 'undone'])
        return jsonify({'total': total, 'completed': completed, 'undone': undone, 'pending': 0, 'success_rate': f"{(completed/total*100):.0f}%" if total else "0%"})

    @app.route('/api/history/<int:movement_id>/undo', methods=['POST'])
    def undo_movement_route(movement_id):
        history = load_history()
        movement = next((h for h in history if h.get('id') == movement_id), None)
        if not movement or movement.get('status') == 'undone': return jsonify({'error': 'Invalid'}), 400
        try:
            from_path = Path(movement['toPath'])
            to_path = Path(movement['fromPath'])
            if from_path.exists():
                to_path.parent.mkdir(parents=True, exist_ok=True)
                if to_path.exists(): os.remove(to_path)
                import shutil
                shutil.move(str(from_path), str(to_path))
                movement['status'] = 'undone'
                save_history(history)
                return jsonify({'success': True, 'movement': movement})
            return jsonify({'error': 'File missing'}), 404
        except Exception as e: return jsonify({'error': str(e)}), 500

    @app.route('/api/history/<int:movement_id>/open', methods=['POST'])
    def open_location(movement_id):
        history = load_history()
        movement = next((h for h in history if h.get('id') == movement_id), None)
        if not movement: return jsonify({'error': 'Not found'}), 404
        current_path = movement['toPath'] if movement.get('status') == 'completed' else movement['fromPath']
        return jsonify({'directory': str(Path(current_path).parent)})