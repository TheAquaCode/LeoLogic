"""
API Routes for File Organizer
"""

import os
import json
import time
from pathlib import Path
from flask import request, jsonify
from config.settings import CONFIG_FILE
from .state import state
from .file_watcher import start_watching, stop_watching
from .file_processor import process_file
from .rag_generator import RAGGenerator


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
            "initialized": state.is_initialized,
            "stats": state.processing_stats
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
            "status": "Active"
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
            "path": data.get("path")
        }
        state.categories.append(category)
        save_config()
        return jsonify(category)

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
    
    # RAG Search (for chatbot integration)
    @app.route("/api/rag/search", methods=["POST"])
    def search_rag():
        query = request.json.get("query", "")
        max_results = request.json.get("max_results", 5)
        
        if not query:
            return jsonify({"error": "Query required"}), 400
        
        results = RAGGenerator.search_rag(query, max_results)
        return jsonify({"results": results})
    
    # Get processing statistics
    @app.route("/api/stats", methods=["GET"])
    def get_stats():
        return jsonify(state.processing_stats)
