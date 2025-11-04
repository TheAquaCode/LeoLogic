"""
AI Model Initialization - Ollama + Whisper
"""

import ollama
from faster_whisper import WhisperModel
from config.settings import PHI3_MODEL, LLAVA_MODEL, WHISPER_MODEL, OLLAMA_HOST
from .state import state


def initialize_models():
    """Initialize Ollama and Whisper models"""
    print("🔄 Initializing AI models...")
    
    try:
        # Initialize Ollama client
        state.ollama_client = ollama.Client(host=OLLAMA_HOST)
        
        # Check if models are available
        print(f"📦 Checking Ollama models...")
        available_models = state.ollama_client.list()
        model_names = [m['name'] for m in available_models['models']]
        
        if PHI3_MODEL not in model_names:
            print(f"⚠️  {PHI3_MODEL} not found. Run: ollama pull {PHI3_MODEL}")
        else:
            print(f"✅ {PHI3_MODEL} ready")
        
        if LLAVA_MODEL not in model_names:
            print(f"⚠️  {LLAVA_MODEL} not found. Run: ollama pull {LLAVA_MODEL}")
        else:
            print(f"✅ {LLAVA_MODEL} ready")
        
        # Initialize Whisper
        print(f"🔄 Loading Whisper {WHISPER_MODEL} model...")
        state.whisper_model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        print(f"✅ Whisper {WHISPER_MODEL} ready")
        
        state.is_initialized = True
        print("✅ All AI models initialized")
        
    except Exception as e:
        print(f"❌ Error initializing models: {e}")
        print("Make sure Ollama is running: ollama serve")
        state.is_initialized = False
