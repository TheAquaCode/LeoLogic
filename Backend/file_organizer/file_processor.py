"""
File Processing Pipeline
1. Check File Size
2. Extract content
3. Analyze with AI
4. Move file based on classification or fallback
5. Generate RAG document at new location
6. Log to history
"""

import shutil
import json
import os
from pathlib import Path
from datetime import datetime
from config.settings import CONFIDENCE_THRESHOLD, DATA_DIR, BASE_DIR, get_confidence_threshold, load_user_settings
from utils.logger import setup_logger

logger = setup_logger(__name__)
from .state import state
from .file_extractors import MultiModalExtractor
from .ai_processor import AIProcessor
from .rag_generator import RAGGenerator

# History file path
HISTORY_FILE = DATA_DIR / "file_history.json"


def add_to_history(movement_data):
    """Add a file movement to history"""
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = []
        
        history.append(movement_data)
        
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Added movement to history: {movement_data['filename']}")
    except Exception as e:
        logger.error(f"Error adding to history: {e}")


def process_file(file_path: str, folder_id: int):
    """
    Standard File Processing:
    Moves file from source to destination based on AI classification.
    """
    try:
        path_obj = Path(file_path)
        
        # 0. Basic Existence Check
        if not path_obj.exists():
            return {"status": "skipped", "file_name": path_obj.name, "error": "File not found"}

        logger.info(f"Processing file: {path_obj.name}")
        
        # Update folder activity timestamp
        if folder_id:
            state.update_folder_activity(folder_id)
        
        # Load Settings
        user_settings = load_user_settings() or {}
        fallback_behavior = user_settings.get('fallbackBehavior', 'Skip file')
        
        # --- MAX FILE SIZE CHECK ---
        # Default to 500MB if not set
        max_size_mb = user_settings.get('maxFileSize', 500)
        file_size_mb = path_obj.stat().st_size / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            logger.warning(f"Skipping file {path_obj.name}: Size {file_size_mb:.2f}MB exceeds limit of {max_size_mb}MB")
            return {
                "status": "skipped",
                "file_name": path_obj.name,
                "error": f"File size ({file_size_mb:.1f}MB) exceeds limit ({max_size_mb}MB)"
            }
        # ---------------------------

        # 1. Extract
        extracted_data = MultiModalExtractor.extract(file_path)

        # 2. Analyze
        ai_analysis = AIProcessor.analyze_content(extracted_data)

        # 3. Classify
        classification = AIProcessor.classify_into_categories(
            ai_analysis, state.categories, filename=path_obj.name
        )

        category_name = classification["category"]
        confidence = classification["confidence"]
        
        # Normalize confidence
        try:
            confidence = float(confidence)
            if confidence > 1.0: confidence /= 100.0
        except:
            confidence = 0.0

        # Determine threshold
        raw_ft = (extracted_data.get("file_type") or "").lower()
        if raw_ft in ("image", "images", "img", "picture", "photo"): key = "images"
        elif raw_ft in ("video", "movies", "mp4", "mov"): key = "video"
        elif raw_ft in ("audio", "sound", "mp3", "wav"): key = "audio"
        else: key = "text"

        try:
            threshold = float(get_confidence_threshold(key))
        except:
            threshold = float(CONFIDENCE_THRESHOLD or 0.3)

        # Determine Destination
        original_path = str(path_obj.absolute())
        dest_folder = None
        final_category = "Uncategorized"
        
        # Check Category Match
        if category_name and confidence >= threshold:
            category = next((c for c in state.categories if c["name"] == category_name), None)
            if category:
                dest_folder = Path(category["path"])
                final_category = category_name
        
        # Check Fallback
        elif fallback_behavior == 'Move to review folder':
            logger.info("Low confidence. Moving to Review folder.")
            dest_folder = BASE_DIR / "Review"
            final_category = "Review"

        # EXECUTE MOVE
        if dest_folder:
            # Ensure destination folder exists
            dest_folder.mkdir(parents=True, exist_ok=True)
            
            dest_path = dest_folder / path_obj.name
            
            # Simple Move (Overwrite if exists, matching standard 'Move' behavior)
            if dest_path.exists() and dest_path != path_obj:
                try:
                    os.remove(dest_path)
                except Exception as e:
                    logger.warning(f"Could not remove existing destination file: {e}")

            shutil.move(file_path, dest_path)
            
            logger.info(f"Moved to: {dest_path}")
            
            # Generate RAG at new location
            RAGGenerator.create_rag_document(
                str(dest_path),
                extracted_data,
                ai_analysis,
                final_category
            )

            # Log History
            history_entry = {
                "id": int(datetime.now().timestamp() * 1000),
                "filename": dest_path.name,
                "fromPath": original_path,
                "toPath": str(dest_path),
                "category": final_category,
                "confidence": f"{confidence:.0%}",
                "detection": f"AI Classification: {final_category}",
                "timestamp": datetime.now().timestamp(),
                "status": "completed"
            }
            add_to_history(history_entry)
            
            state.processing_stats["total"] += 1
            state.processing_stats["success"] += 1
            
            return {
                "status": "success",
                "file_name": dest_path.name,
                "category": final_category,
                "confidence": confidence,
                "destination": str(dest_path)
            }

        # Skip File (Low confidence & no fallback move)
        state.processing_stats["total"] += 1
        
        # Create RAG in place
        RAGGenerator.create_rag_document(
            file_path,
            extracted_data,
            ai_analysis,
            "Uncategorized"
        )

        return {
            "status": "low_confidence",
            "file_name": path_obj.name,
            "confidence": confidence,
            "destination": file_path
        }

    except Exception as e:
        logger.error(f"Processing error: {e}", exc_info=True)
        return {"status": "error", "file_name": Path(file_path).name, "error": str(e)}