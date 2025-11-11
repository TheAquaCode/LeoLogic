"""
API Routes for Chatbot
"""

import time
from flask import request, jsonify


def register_routes(app, chatbot):
    """Register all chatbot API routes"""

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify(
            {
                "status": "online",
                "model_ready": chatbot.is_ready,
                "loading": chatbot.loading,
            }
        )

    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.json
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        if not chatbot.is_ready:
            return jsonify(
                {"response": "Ollama is still initializing...", "model_ready": False}
            )

        start_time = time.time()
        response = chatbot.generate_response(user_message)
        elapsed = round(time.time() - start_time, 2)

        return jsonify(
            {
                "response": response,
                "model_ready": chatbot.is_ready,
                "elapsed_time": elapsed,
            }
        )

    @app.route("/clear", methods=["POST"])
    def clear_history():
        chatbot.clear_history()
        return jsonify({"status": "success", "message": "Conversation history cleared"})

    @app.route("/status", methods=["GET"])
    def get_status():
        return jsonify(
            {
                "conversation_length": len(chatbot.conversation_history),
                "model_ready": chatbot.is_ready,
            }
        )

    @app.route("/test-rag", methods=["POST"])
    def test_rag():
        """Test endpoint to see what RAG files are available and test search"""
        data = request.json
        query = data.get("query", "")

        if not query:
            # If no query, just show available RAG files
            from pathlib import Path
            from config.settings import RAG_DATA_DIR

            rag_dir = Path(RAG_DATA_DIR)
            if not rag_dir.exists():
                return jsonify(
                    {
                        "error": f"RAG directory does not exist: {rag_dir}",
                        "rag_files": [],
                    }
                )

            rag_files = list(rag_dir.glob("*.rag.json"))
            return jsonify(
                {
                    "rag_directory": str(rag_dir),
                    "total_files": len(rag_files),
                    "rag_files": [f.name for f in rag_files],
                }
            )

        # Test the RAG search
        start_time = time.time()
        results = chatbot._direct_rag_search(query, max_results=5)
        elapsed = round(time.time() - start_time, 3)

        return jsonify(
            {
                "query": query,
                "results_found": len(results),
                "search_time": elapsed,
                "results": results,
            }
        )
