"""
Configuration Settings
"""

import os
import json
import hashlib
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Organized data storage
RAG_DATA_DIR = DATA_DIR / "rag_data"
RAG_DATA_DIR.mkdir(exist_ok=True)

LOGS_DIR = DATA_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

MOVE_LOGS_DIR = LOGS_DIR / "move_reports"
MOVE_LOGS_DIR.mkdir(exist_ok=True)

# Ports
FILE_ORGANIZER_PORT = 5001
CHATBOT_PORT = 5000

# File Organizer Settings
CONFIG_FILE = DATA_DIR / "file_organizer_config.json"
SETTINGS_FILE = DATA_DIR / "app_settings.json"

# Default confidence thresholds (can be overridden by user settings)
DEFAULT_CONFIDENCE_THRESHOLDS = {
    "text": 0.85,
    "images": 0.80,
    "audio": 0.75,
    "video": 0.70
}

# Global confidence threshold (fallback)
CONFIDENCE_THRESHOLD = 0.3

# Processing Settings
MAX_WORKERS = 4  # Multi-threaded processing
PROCESSING_BATCH_SIZE = 10  # Files per batch

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
ENABLE_RAG_CACHING = True  # Skip re-scanning if RAG exists

# Chatbot Settings
MAX_CONVERSATION_HISTORY = 3
ENABLE_RAG = True

# Logging Settings
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5


def load_user_settings():
    """Load user settings from file"""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading settings: {e}")
    return None


def save_user_settings(settings):
    """Save user settings to file"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"⚠️ Error saving settings: {e}")
        return False


def get_confidence_threshold(file_type):
    """Get confidence threshold for a specific file type"""
    settings = load_user_settings()
    
    if settings and 'confidenceThresholds' in settings:
        threshold_percent = settings['confidenceThresholds'].get(file_type, 85)
        return threshold_percent / 100.0
    
    # Fallback to defaults
    return DEFAULT_CONFIDENCE_THRESHOLDS.get(file_type, 0.85)


def get_settings_hash():
    """
    Generate a hash of the current settings that affect processing.
    Used to determine if files should be re-processed.
    """
    settings = load_user_settings() or {}
    
    # Extract relevant keys that affect decision making
    relevant = {
        'confidenceThresholds': settings.get('confidenceThresholds', {}),
        'modelToggles': settings.get('modelToggles', {}),
        'fallbackBehavior': settings.get('fallbackBehavior', ''),
        'skipHiddenFiles': settings.get('skipHiddenFiles', True)
    }
    
    # Create hash
    s = json.dumps(relevant, sort_keys=True)
    return hashlib.md5(s.encode()).hexdigest()