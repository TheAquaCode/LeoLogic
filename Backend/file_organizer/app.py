"""
File Organizer Flask Application
"""

from flask import Flask
from flask_cors import CORS
from .models import initialize_models
from .routes import register_routes, load_config
from .file_watcher import start_all_watchers


def create_file_organizer_app():
    """Create and configure the file organizer Flask app"""
    app = Flask(__name__)
    CORS(app)
    
    # Initialize AI models
    initialize_models()
    
    # Load configuration
    load_config()
    
    # Register API routes
    register_routes(app)
    
    # Start file watchers
    start_all_watchers()
    
    print("📡 File Organizer API ready")
    print("Endpoints:")
    print("  GET  /api/health")
    print("  GET  /api/watched-folders")
    print("  POST /api/watched-folders")
    print("  POST /api/watched-folders/<id>/toggle")
    print("  GET  /api/categories")
    print("  POST /api/categories")
    print("  POST /api/process-folder/<id>")
    print("  POST /api/rag/search")
    print("  GET  /api/stats")
    
    return app
