"""
Configuration Settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# RAG storage
RAG_DIR = DATA_DIR / "rag_store"
RAG_DIR.mkdir(exist_ok=True)

# Ports
FILE_ORGANIZER_PORT = 5001
CHATBOT_PORT = 5000

# File Organizer Settings
CONFIG_FILE = DATA_DIR / "file_organizer_config.json"
CONFIDENCE_THRESHOLD = 0.3

# Ollama Settings (Local AI)
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
PHI3_MODEL = "phi3:mini"  # Text processing
LLAVA_MODEL = "llava-phi3"  # Image processing

# Whisper Settings (Audio/Video)
WHISPER_MODEL = "tiny"  # Options: tiny, base, small, medium, large

# RAG Settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_RAG_RESULTS = 5

# Chatbot Settings
MAX_CONVERSATION_HISTORY = 3
ENABLE_RAG = True
