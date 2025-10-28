"""
API Routes for Chatbot
"""

import time
from flask import request, jsonify


def register_routes(app, chatbot):
    """Register all chatbot API routes"""
    
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "online",
            "model_ready": chatbot.is_ready,
            "loading": chatbot.loading
        })

    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.json
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        if not chatbot.is_ready:
            return jsonify({
                "response": "Mistral API is still initializing...",
                "model_ready": False
            })

        start_time = time.time()
        response = chatbot.generate_response(user_message)
        elapsed = round(time.time() - start_time, 2)

        return jsonify({
            "response": response,
            "model_ready": chatbot.is_ready,
            "elapsed_time": elapsed
        })

    @app.route("/clear", methods=["POST"])
    def clear_history():
        chatbot.clear_history()
        return jsonify({
            "status": "success",
            "message": "Conversation history cleared"
        })

    @app.route("/status", methods=["GET"])
    def get_status():
        return jsonify({
            "conversation_length": len(chatbot.conversation_history),
            "model_ready": chatbot.is_ready
        })
