"""
File Processing and Classification
"""

import json
import shutil
import time
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
        # Import here to avoid circular import
        from .file_history import file_history
        
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
                
                # Store original path before moving
                original_path = str(Path(file_path).resolve())
                
                # Move the file
                shutil.move(file_path, dest_path)
                
                # Format paths for better console output
                def format_path_for_console(path):
                    """Show root/.../parent/file.ext format"""
                    parts = Path(path).parts
                    if len(parts) <= 3:
                        return str(path)
                    return f"{parts[0]}/...../{parts[-2]}/{parts[-1]}"
                
                from_display = format_path_for_console(original_path)
                to_display = format_path_for_console(str(dest_path))
                
                print(f"✅ Moved: {from_display} → {to_display} (conf={confidence:.2f})")
                
                # Track the movement in history
                file_history.add_movement(
                    file_name=dest_path.name,
                    from_path=original_path,
                    to_path=str(dest_path),
                    category=category['name'],
                    confidence=confidence,
                    detection="AI Classification"
                )
                
                # Save chunks as JSON for RAG in dedicated directory
                from config.settings import DATA_DIR
                rag_dir = DATA_DIR / "rag_files"
                rag_dir.mkdir(exist_ok=True)
                
                # Use file hash or unique name to avoid conflicts
                rag_filename = f"{dest_path.stem}_{int(time.time())}.rag.json"
                rag_path = rag_dir / rag_filename
                
                with open(rag_path, "w") as f:
                    json.dump({
                        "chunks": chunks, 
                        "original_file": str(dest_path),
                        "category": category['name'],
                        "confidence": confidence,
                        "timestamp": time.time()
                    }, f, indent=2)
                
                print(f"📝 RAG file saved: {rag_path}")
                
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
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "file_name": Path(file_path).name,
            "error": str(e)
        }