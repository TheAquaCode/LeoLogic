"""
File Processing Pipeline
1. Check Settings & File constraints
2. Extract content & Analyze with AI
3. Determine Destination
4. Create Backup (If enabled AND file is about to move)
5. Move file
6. Update Metadata (if needed)
7. Generate RAG & Log
"""

import shutil
import json
import os
import stat
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

def is_hidden(path_obj):
    """Check if file is hidden (Dot file or Windows attribute)"""
    # Dot file check (Mac/Linux)
    if path_obj.name.startswith('.'):
        return True
    
    # Windows attribute check
    if os.name == 'nt':
        try:
            attrs = path_obj.stat().st_file_attributes
            if attrs & stat.FILE_ATTRIBUTE_HIDDEN:
                return True
        except:
            pass
    return False

def process_file(file_path: str, folder_id: int):
    try:
        path_obj = Path(file_path)
        
        # 0. Basic Existence Check
        if not path_obj.exists():
            return {"status": "skipped", "file_name": path_obj.name, "error": "File not found"}

        # Load Settings
        user_settings = load_user_settings() or {}
        fallback_behavior = user_settings.get('fallbackBehavior', 'Skip file')
        max_size_mb = user_settings.get('maxFileSize', 500)
        skip_hidden = user_settings.get('skipHiddenFiles', True)
        create_backups = user_settings.get('createBackups', False)
        preserve_metadata = user_settings.get('preserveMetadata', True)

        logger.info(f"Processing: {path_obj.name} | Backups: {create_backups}")

        # 1. Skip Hidden Files
        if skip_hidden and is_hidden(path_obj):
            logger.info(f"Skipping hidden file: {path_obj.name}")
            return {"status": "skipped", "file_name": path_obj.name, "error": "Hidden file"}

        # 2. Check File Size
        file_size_mb = path_obj.stat().st_size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            logger.warning(f"Skipping file {path_obj.name}: Size {file_size_mb:.2f}MB exceeds limit")
            return {"status": "skipped", "file_name": path_obj.name, "error": "File size limit exceeded"}
        
        if folder_id: state.update_folder_activity(folder_id)

        # 3. Extract & Analyze
        extracted_data = MultiModalExtractor.extract(file_path)
        ai_analysis = AIProcessor.analyze_content(extracted_data)
        classification = AIProcessor.classify_into_categories(
            ai_analysis, state.categories, filename=path_obj.name
        )

        category_name = classification["category"]
        confidence = float(classification["confidence"])
        if confidence > 1.0: confidence /= 100.0

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
        
        if category_name and confidence >= threshold:
            category = next((c for c in state.categories if c["name"] == category_name), None)
            if category:
                dest_folder = Path(category["path"])
                final_category = category_name
        
        elif fallback_behavior == 'Move to review folder':
            dest_folder = BASE_DIR / "Review"
            final_category = "Review"

        # 4. Execute Move (With Backup Logic)
        if dest_folder:
            dest_folder.mkdir(parents=True, exist_ok=True)
            dest_path = dest_folder / path_obj.name
            
            # --- BACKUP LOGIC STARTS HERE ---
            if create_backups:
                try:
                    # Create daily backup folder: Backend/data/backups/2023-10-27/
                    date_str = datetime.now().strftime("%Y-%m-%d")
                    backup_dir = DATA_DIR / "backups" / date_str
                    backup_dir.mkdir(parents=True, exist_ok=True)
                    
                    backup_path = backup_dir / path_obj.name
                    
                    # Avoid overwriting existing backups for the same filename (append timestamp)
                    if backup_path.exists():
                        ts = int(datetime.now().timestamp())
                        backup_path = backup_dir / f"{path_obj.stem}_{ts}{path_obj.suffix}"

                    shutil.copy2(file_path, backup_path)
                    logger.info(f"✅ Backup saved to: {backup_path}")
                except Exception as e:
                    logger.error(f"❌ Backup failed: {e}")
            # --- BACKUP LOGIC ENDS HERE ---

            # Handle Collision (Overwrite)
            if dest_path.exists() and dest_path != path_obj:
                try: os.remove(dest_path)
                except: pass

            shutil.move(file_path, dest_path)
            
            # Metadata Handling (Preserve Metadata toggle)
            if not preserve_metadata:
                try:
                    # 'touch' the file to update mtime to now
                    os.utime(dest_path, None)
                    logger.debug("Metadata reset (Preserve Metadata = False)")
                except: pass
            
            # Generate RAG
            RAGGenerator.create_rag_document(
                str(dest_path), extracted_data, ai_analysis, final_category
            )

            # Log History
            add_to_history({
                "id": int(datetime.now().timestamp() * 1000),
                "filename": dest_path.name,
                "fromPath": original_path,
                "toPath": str(dest_path),
                "category": final_category,
                "confidence": f"{confidence:.0%}",
                "detection": f"AI Classification: {final_category}",
                "timestamp": datetime.now().timestamp(),
                "status": "completed"
            })
            
            state.processing_stats["total"] += 1
            state.processing_stats["success"] += 1
            
            return {
                "status": "success",
                "file_name": dest_path.name,
                "category": final_category,
                "confidence": confidence,
                "destination": str(dest_path)
            }

        # Skip File
        state.processing_stats["total"] += 1
        
        # Create RAG in place
        RAGGenerator.create_rag_document(
            file_path, extracted_data, ai_analysis, "Uncategorized"
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