"""
AI Model Initialization - Ollama + Whisper
"""

import ollama
from faster_whisper import WhisperModel
from config.settings import PHI3_MODEL, LLAVA_MODEL, WHISPER_MODEL, OLLAMA_HOST
from .state import state
from utils.logger import setup_logger

logger = setup_logger(__name__)


def initialize_models():
    """Initialize Ollama and Whisper models"""
    logger.info("Initializing AI models...")
    
    try:
        # Initialize Ollama client
        state.ollama_client = ollama.Client(host=OLLAMA_HOST)
        
        # Check if models are available
        logger.info("Checking Ollama models...")
        available_models = state.ollama_client.list()
        model_names = []
        if 'models' in available_models:
            for m in available_models['models']:
                if isinstance(m, dict) and 'name' in m:
                    model_names.append(m['name'])
                elif isinstance(m, dict) and 'model' in m:
                    model_names.append(m['model'])
                elif hasattr(m, 'name'):
                    model_names.append(m.name)
                elif hasattr(m, 'model'):
                    model_names.append(m.model)
        
        if PHI3_MODEL not in model_names:
            logger.warning(f"{PHI3_MODEL} not found. Run: ollama pull {PHI3_MODEL}")
        else:
            logger.info(f"{PHI3_MODEL} ready")
        
        if LLAVA_MODEL not in model_names:
            logger.warning(f"{LLAVA_MODEL} not found. Run: ollama pull {LLAVA_MODEL}")
        else:
            logger.info(f"{LLAVA_MODEL} ready")
        
        # Initialize Whisper
        logger.info(f"Loading Whisper {WHISPER_MODEL} model...")
        state.whisper_model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        logger.info(f"Whisper {WHISPER_MODEL} ready")
        
        state.is_initialized = True
        logger.info("All AI models initialized")
        
    except Exception as e:
        logger.error(f"Error initializing models: {e}", exc_info=True)
        logger.error("Make sure Ollama is running: ollama serve")
        state.is_initialized = False
