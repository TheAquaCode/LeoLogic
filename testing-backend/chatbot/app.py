"""
Chatbot Flask Application
"""

from flask import Flask
from flask_cors import CORS
from .mistral_client import MistralChatbot
from .routes import register_routes


def create_chatbot_app():
    """Create and configure the chatbot Flask app"""
    app = Flask(__name__)
    CORS(app)
    
    # Initialize chatbot
    chatbot = MistralChatbot()
    
    # Register API routes
    register_routes(app, chatbot)
    
    print("📡 Chatbot API ready")
    print("Endpoints:")
    print("  GET  /health")
    print("  GET  /status")
    print("  POST /chat")
    print("  POST /clear")
    
    return app
