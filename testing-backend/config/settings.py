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

# API Keys
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")

# Ports
FILE_ORGANIZER_PORT = 5001
CHATBOT_PORT = 5000

# File Organizer Settings
CONFIG_FILE = DATA_DIR / "file_organizer_config.json"
CONFIDENCE_THRESHOLD = 0.3
BART_MODEL_NAME = "facebook/bart-large-mnli"

# Chatbot Settings
MISTRAL_MODEL = "mistral-large-2411"
MAX_CONVERSATION_HISTORY = 3  # Keep last N exchanges
