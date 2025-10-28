"""
AI File Sorter Backend (BART + RAG)
-----------------------------------
Handles watched folders, categories, file monitoring, and AI-powered organization.
Ensures safe API responses for frontend (.map() errors fixed).
"""

import os
import json
import time
import shutil
from pathlib import Path
from datetime import datetime
from threading import Thread, Lock
from typing import List

from flask import Flask, request, jsonify
from flask_cors import CORS
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# NLP / ML
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

# File extraction
import PyPDF2
from docx import Document
import pytesseract
from PIL import Image

app = Flask(__name__)
CORS(app)

# Global state
class FileOrganizerState:
    def __init__(self):
        self.watched_folders = []
        self.categories = []
        self.observers = {}
        self.lock = Lock()
        self.processing_queue = []
        self.bart_classifier = None
        self.is_initialized = False

state = FileOrganizerState()

# Config
CONFIG_FILE = "file_organizer_config.json"
CONFIDENCE_THRESHOLD = 0.3

# ============================================
# INITIALIZATION
# ============================================

def initialize_models():
    """Load BART model for classification"""
    print("🔄 Loading BART model for classification...")
    model_name = "facebook/bart-large-mnli"
    state.bart_classifier = pipeline("zero-shot-classification", model=model_name)
    state.is_initialized = True
    print("✅ BART model loaded")

def load_config():
    """Load watched folders and categories from disk"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            state.watched_folders = config.get("watched_folders", [])
            state.categories = config.get("categories", [])
            print(f"📂 Loaded {len(state.watched_folders)} watched folders")
            print(f"🏷️  Loaded {len(state.categories)} categories")

def save_config():
    """Save watched folders and categories"""
    config = {
        "watched_folders": state.watched_folders,
        "categories": state.categories
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

# ============================================
# FILE EXTRACTION
# ============================================

def extract_text_from_file(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    try:
        if ext in ['.txt', '.md', '.csv']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        elif ext == '.pdf':
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
            return text
        elif ext == '.docx':
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            img = Image.open(file_path)
            return pytesseract.image_to_string(img)
        else:
            return Path(file_path).stem
    except Exception as e:
        print(f"⚠️ Error extracting {file_path}: {e}")
        return Path(file_path).stem

def chunk_text(text: str, max_length=1000, overlap=100) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_length
        chunks.append(text[start:end])
        start += max_length - overlap
    return chunks

# ============================================
# FILE SORTING
# ============================================

def classify_file(text: str) -> dict:
    """Use BART to classify file into user categories"""
    if not state.categories:
        return {"category": None, "score": 0.0}
    
    candidate_labels = [c['name'] for c in state.categories]
    result = state.bart_classifier(text, candidate_labels, multi_label=False)
    top_label = result['labels'][0]
    top_score = result['scores'][0]
    return {"category": top_label, "score": top_score}

def process_file(file_path: str, folder_id: int):
    try:
        text = extract_text_from_file(file_path)
        if not text.strip():
            print(f"⚠️ Skipping empty file: {file_path}")
            return
        
        chunks = chunk_text(text)
        classification = classify_file(text)
        best_category_name = classification["category"]
        confidence = classification["score"]
        
        if best_category_name and confidence >= CONFIDENCE_THRESHOLD:
            category = next((c for c in state.categories if c['name'] == best_category_name), None)
            if category:
                dest_folder = Path(category['path'])
                dest_folder.mkdir(parents=True, exist_ok=True)
                dest_path = dest_folder / Path(file_path).name
                counter = 1
                while dest_path.exists():
                    dest_path = dest_folder / f"{Path(file_path).stem}_{counter}{Path(file_path).suffix}"
                    counter += 1
                shutil.move(file_path, dest_path)
                print(f"✅ Moved {file_path} -> {dest_path} (conf={confidence:.2f})")
                # Save chunks as JSON for RAG later
                rag_path = dest_path.with_suffix(".rag.json")
                with open(rag_path, "w") as f:
                    json.dump({"chunks": chunks, "original_file": str(dest_path)}, f, indent=2)
                return {"status": "success", "file_name": dest_path.name, "category": category["name"], "confidence": confidence}
        
        print(f"⚠️ Low confidence ({confidence:.2f}) for {file_path}")
        return {"status": "low_confidence", "file_name": Path(file_path).name, "confidence": confidence}
    
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return {"status": "error", "file_name": Path(file_path).name, "error": str(e)}

# ============================================
# FILE SYSTEM WATCHER
# ============================================

class FileHandler(FileSystemEventHandler):
    def __init__(self, folder_id):
        self.folder_id = folder_id
        super().__init__()
    
    def on_created(self, event):
        if not event.is_directory:
            with state.lock:
                state.processing_queue.append({"file_path": event.src_path, "folder_id": self.folder_id})
            print(f"📥 New file detected: {event.src_path}")

def start_watching(folder_id: int, folder_path: str):
    if folder_id in state.observers:
        return
    handler = FileHandler(folder_id)
    observer = Observer()
    observer.schedule(handler, folder_path, recursive=False)
    observer.start()
    state.observers[folder_id] = observer
    print(f"👀 Watching folder: {folder_path}")

def stop_watching(folder_id: int):
    if folder_id in state.observers:
        state.observers[folder_id].stop()
        state.observers[folder_id].join()
        del state.observers[folder_id]

def process_queue_worker():
    while True:
        if state.processing_queue:
            with state.lock:
                item = state.processing_queue.pop(0)
            process_file(item["file_path"], item["folder_id"])
        time.sleep(1)

# ============================================
# API ENDPOINTS
# ============================================

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "initialized": state.is_initialized})

# Watched Folders
@app.route("/api/watched-folders", methods=["GET"])
def get_folders():
    return jsonify(state.watched_folders)  # Always return array

@app.route("/api/watched-folders", methods=["POST"])
def add_folder():
    data = request.json
    folder = {
        "id": int(time.time() * 1000),
        "name": data.get("name"),
        "path": data.get("path"),
        "status": "Active"
    }
    state.watched_folders.append(folder)
    save_config()
    start_watching(folder["id"], folder["path"])
    return jsonify(folder)

@app.route("/api/watched-folders/<int:folder_id>/toggle", methods=["POST"])
def toggle_folder(folder_id):
    folder = next((f for f in state.watched_folders if f["id"] == folder_id), None)
    if folder:
        folder["status"] = "Paused" if folder["status"] == "Active" else "Active"
        if folder["status"] == "Active":
            start_watching(folder["id"], folder["path"])
        else:
            stop_watching(folder["id"])
        save_config()
        return jsonify(folder)
    return jsonify({"error": "Folder not found"}), 404

# Categories
@app.route("/api/categories", methods=["GET"])
def get_categories():
    return jsonify(state.categories)  # Always return array

@app.route("/api/categories", methods=["POST"])
def add_category():
    data = request.json
    category = {
        "id": int(time.time() * 1000),
        "name": data.get("name"),
        "path": data.get("path")
    }
    state.categories.append(category)
    save_config()
    return jsonify(category)

# Manual folder processing
@app.route("/api/process-folder/<int:folder_id>", methods=["POST"])
def process_folder(folder_id):
    folder = next((f for f in state.watched_folders if f["id"] == folder_id), None)
    if not folder or not Path(folder["path"]).exists():
        return jsonify({"error": "Folder not found"}), 404
    results = []
    for file_path in Path(folder["path"]).glob("*"):
        if file_path.is_file():
            results.append(process_file(str(file_path), folder_id))
    return jsonify({"processed": len(results), "results": results})

# ============================================
# STARTUP
# ============================================

if __name__ == "__main__":
    load_config()
    initialize_models()
    
    # Start background queue
    t = Thread(target=process_queue_worker, daemon=True)
    t.start()
    
    # Start watching all active folders
    for folder in state.watched_folders:
        if folder.get("status") == "Active" and Path(folder["path"]).exists():
            start_watching(folder["id"], folder["path"])
    
    app.run(host="0.0.0.0", port=5001)
