"""
Leologic Backend - Main Entry Point
===================================
Boots up both the file organizer and chatbot services.
"""

import os
import sys
from threading import Thread
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from file_organizer.app import create_file_organizer_app
from chatbot.app import create_chatbot_app
from config.settings import FILE_ORGANIZER_PORT, CHATBOT_PORT


def run_file_organizer():
    print(f"🗂️  Starting File Organizer on port {FILE_ORGANIZER_PORT}...")
    app = create_file_organizer_app()
    app.run(host="0.0.0.0", port=FILE_ORGANIZER_PORT, debug=False, use_reloader=False)


def run_chatbot():
    """Run chatbot service on port 5000"""
    app = create_chatbot_app()
    app.run(host="0.0.0.0", port=CHATBOT_PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    # Start file organizer in separate thread
    organizer_thread = Thread(target=run_file_organizer, daemon=True)
    organizer_thread.start()
    try:
        run_chatbot()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Leologic Backend...")
        sys.exit(0)
