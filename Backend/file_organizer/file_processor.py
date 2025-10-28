"""
File Processing and Classification
"""

import json
import shutil
from pathlib import Path
from config.settings import CONFIDENCE_THRESHOLD
from .state import state
from .file_extractor import extract_text_from_file, chunk_text


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
    """Process a single file: extract, classify, and move"""
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
                
                return {
                    "status": "success",
                    "file_name": dest_path.name,
                    "category": category["name"],
                    "confidence": confidence
                }
        
        print(f"⚠️ Low confidence ({confidence:.2f}) for {file_path}")
        return {
            "status": "low_confidence",
            "file_name": Path(file_path).name,
            "confidence": confidence
        }
    
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return {
            "status": "error",
            "file_name": Path(file_path).name,
            "error": str(e)
        }
