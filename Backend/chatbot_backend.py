
"""
Phi-2 Chatbot Backend (GPU-only Optimized)
------------------------------------------
- Strictly requires NVIDIA GPU
- No CPU fallback
- No repeating 'ready' logs
- Warm-up for faster first response
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import threading
import time
import sys

app = Flask(__name__)
CORS(app)


class Phi2Chatbot:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        self.loading = False
        self.conversation_history = []

        # --- FORCE GPU ONLY ---
        if not torch.cuda.is_available():
            print("❌ GPU not detected! Aborting.")
            sys.exit(1)

        self.device = "cuda"
        print(f"🧠 Using device: {self.device} ({torch.cuda.get_device_name(0)})")

    def load_model(self):
        """Load Phi-2 model with GPU + 4-bit quantization"""
        if self.is_loaded or self.loading:
            return

        self.loading = True
        print("🤖 Loading Phi-2 model on GPU (with 4-bit quantization)...")

        try:
            model_name = "microsoft/phi-2"

            # Safety check — stop immediately if no CUDA
            if not torch.cuda.is_available():
                raise RuntimeError("❌ No GPU detected. Install the CUDA build of PyTorch.")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )

            # Import BitsAndBytes config
            from transformers import BitsAndBytesConfig

            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",  # better accuracy
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.float16
            )

            # Load the model using 4-bit quantization on GPU
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=bnb_config,
                device_map={"": "cuda"},  # force GPU placement
                trust_remote_code=True
            )

            torch.cuda.empty_cache()
            self.is_loaded = True
            self.loading = False
            print("✅ Phi-2 model loaded successfully on GPU (4-bit quantized)!")

        except Exception as e:
            self.loading = False
            print(f"❌ Error loading model: {e}")
            raise

    def generate_response(self, user_message, store_history=True):
        """Generate response from Phi-2."""
        if not self.is_loaded:
            return "Model is still loading, please wait..."

        try:
            context = (
                "You are an AI assistant for a file management application. "
                "Be concise, friendly, and helpful.\n\n"
            )

            # Keep last 3 exchanges
            for msg in self.conversation_history[-3:]:
                context += f"User: {msg['user']}\nAssistant: {msg['assistant']}\n\n"

            prompt = f"{context}User: {user_message}\nAssistant:"

            # Tokenize + send to GPU
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=768
            ).to(self.device)

            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=128,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response.split("Assistant:")[-1].strip()
            if "User:" in response:
                response = response.split("User:")[0].strip()

            if store_history:
                self.conversation_history.append({
                    "user": user_message,
                    "assistant": response
                })

            return response

        except Exception as e:
            print(f"❌ Error generating response: {e}")
            return f"Error: {e}"

    def clear_history(self):
        self.conversation_history = []


# Initialize chatbot
chatbot = Phi2Chatbot()

print("🚀 Starting AI File Sorter Chatbot Backend")
load_thread = threading.Thread(target=chatbot.load_model)
load_thread.daemon = True
load_thread.start()


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint (no log spam)."""
    return jsonify({
        "status": "online",
        "model_loaded": chatbot.is_loaded,
        "loading": chatbot.loading,
        "device": chatbot.device
    })


@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat messages."""
    data = request.json
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    if not chatbot.is_loaded:
        return jsonify({
            "response": "AI model is still loading. Please wait a moment...",
            "model_ready": False
        })

    start_time = time.time()
    response = chatbot.generate_response(user_message)
    elapsed = round(time.time() - start_time, 2)

    return jsonify({
        "response": response,
        "model_ready": chatbot.is_loaded,
        "device": chatbot.device,
        "elapsed_time": elapsed
    })


@app.route("/clear", methods=["POST"])
def clear_history():
    chatbot.clear_history()
    return jsonify({"status": "success", "message": "Conversation history cleared"})


@app.route("/status", methods=["GET"])
def get_status():
    return jsonify({
        "model_loaded": chatbot.is_loaded,
        "loading": chatbot.loading,
        "conversation_length": len(chatbot.conversation_history),
        "device": chatbot.device
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
