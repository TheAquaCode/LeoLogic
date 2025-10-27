"""
Mistral API Chatbot Backend
---------------------------
- Uses Mistral API for inference
- No local GPU required
- Keeps conversation history
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from mistralai import Mistral
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# --- Initialize Mistral client ---
api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise RuntimeError("❌ MISTRAL_API_KEY not set in environment variables.")

client = Mistral(api_key=api_key)


class MistralChatbot:
    def __init__(self):
        self.conversation_history = []
        self.is_ready = True  # API is ready immediately
        self.loading = False
        self.system_instruction = "You are a helpful chatbot for an AI file sorter application. Be concise and friendly."

    def generate_response(self, user_message, store_history=True):
        """Send conversation to Mistral API and get the response."""
        try:
            # Build messages: start with system instruction, then keep last 3 exchanges for context
            messages = [{"role": "system", "content": self.system_instruction}]
            
            for msg in self.conversation_history[-3:]:
                messages.append({"role": "user", "content": msg["user"]})
                messages.append({"role": "assistant", "content": msg["assistant"]})

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Call Mistral API (non-streaming for simplicity)
            chat_response = client.chat.complete(
                model="mistral-large-2411",
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
            )

            # Extract the response text
            response_text = chat_response.choices[0].message.content

            # Save to history
            if store_history:
                self.conversation_history.append({
                    "user": user_message,
                    "assistant": response_text
                })

            return response_text

        except Exception as e:
            print(f"❌ Error generating response: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {str(e)}"

    def clear_history(self):
        self.conversation_history = []


# Initialize chatbot
chatbot = MistralChatbot()


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
    return jsonify({"status": "success", "message": "Conversation history cleared"})


@app.route("/status", methods=["GET"])
def get_status():
    return jsonify({
        "conversation_length": len(chatbot.conversation_history),
        "model_ready": chatbot.is_ready
    })


if __name__ == "__main__":
    print("📡 REST API running on http://localhost:5000")
    print("Endpoints:")
    print("  GET  /health")
    print("  GET  /status")
    print("  POST /chat")
    print("  POST /clear")
    print("\nPress Ctrl+C to stop the server\n")

    app.run(host="0.0.0.0", port=5000, debug=False)