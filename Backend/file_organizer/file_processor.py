"""
File Processing Pipeline with RAG-First Approach
1. Extract content
2. Analyze with AI
3. Create RAG document
4. Read RAG and classify
5. Move file based on RAG classification
"""

import shutil
import json
from pathlib import Path
from config.settings import CONFIDENCE_THRESHOLD
from utils.logger import setup_logger
from utils.move_logger import add_move

logger = setup_logger(__name__)
from .state import state
from .file_extractors import MultiModalExtractor
from .ai_processor import AIProcessor
from .rag_generator import RAGGenerator


def process_file(file_path: str, folder_id: int):
    """
    RAG-first file processing pipeline:
    1. Extract content (text, images, audio)
    2. Analyze with AI
    3. Create RAG document FIRST (regardless of confidence)
    4. Read RAG and classify into category
    5. Move to destination (if confident)
    """
    try:
        # Check if file still exists before processing
        if not Path(file_path).exists():
            logger.warning(f"File no longer exists, skipping: {file_path}")
            return {
                "status": "skipped",
                "file_name": Path(file_path).name,
                "error": "File not found",
            }

        logger.info(
            f"Processing file: {Path(file_path).name}", extra={"file_path": file_path}
        )

        # Step 1: Extract all content
        logger.debug("Extracting content...")
        extracted_data = MultiModalExtractor.extract(file_path)

        # Step 2: Analyze with AI
        logger.debug("Analyzing with AI...")
        ai_analysis = AIProcessor.analyze_content(extracted_data)

        # Step 3: Create RAG document FIRST (at original location)
        logger.debug("Creating RAG document...")
        rag_path = RAGGenerator.create_rag_document(
            file_path,
            extracted_data,
            ai_analysis,
            "Uncategorized",  # Temporary, will update after classification
        )

        if not rag_path:
            logger.warning("RAG creation failed, continuing with classification...")

        # Step 4: Read the RAG file we just created and use it for classification
        logger.debug("Reading RAG for classification...")

        # Load the RAG document
        if rag_path and Path(rag_path).exists():
            with open(rag_path, "r", encoding="utf-8") as f:
                rag_data = json.load(f)

            # Use RAG data for classification (it has the full analysis)
            classification = AIProcessor.classify_into_categories(
                rag_data["analysis"], state.categories, filename=Path(file_path).name
            )
        else:
            # Fallback: use the analysis directly if RAG failed
            classification = AIProcessor.classify_into_categories(
                ai_analysis, state.categories
            )

        category_name = classification["category"]
        confidence = classification["confidence"]

        # Track the final file path
        final_file_path = file_path
        final_rag_path = rag_path

        # Step 5: Move file if confidence is high enough
        if category_name and confidence >= CONFIDENCE_THRESHOLD:
            category = next(
                (c for c in state.categories if c["name"] == category_name), None
            )

            if category:
                # Move file to destination folder
                dest_folder = Path(category["path"])
                dest_folder.mkdir(parents=True, exist_ok=True)
                dest_path = dest_folder / Path(file_path).name

                # Handle duplicates
                counter = 1
                while dest_path.exists():
                    dest_path = (
                        dest_folder
                        / f"{Path(file_path).stem}_{counter}{Path(file_path).suffix}"
                    )
                    counter += 1

                # Move the file
                shutil.move(file_path, dest_path)
                final_file_path = str(dest_path)

                logger.info(f"Successfully moved to: {dest_path}")
                logger.info(f"Confidence: {confidence:.2%}")

                # Update the RAG document with new file path and correct category
                if rag_path and Path(rag_path).exists():
                    with open(rag_path, "r", encoding="utf-8") as f:
                        rag_doc = json.load(f)

                    # Update file info
                    rag_doc["file_info"]["original_path"] = final_file_path
                    rag_doc["file_info"]["category"] = category_name

                    # Save updated RAG
                    with open(rag_path, "w", encoding="utf-8") as f:
                        json.dump(rag_doc, f, indent=2, ensure_ascii=False)

                    logger.debug(f"Updated RAG with new path and category")

                # Update stats
                state.processing_stats["total"] += 1
                state.processing_stats["success"] += 1
                file_type = extracted_data.get("file_type", "other")
                state.processing_stats["by_type"][file_type] = (
                    state.processing_stats["by_type"].get(file_type, 0) + 1
                )

                return {
                    "status": "success",
                    "file_name": Path(final_file_path).name,
                    "category": category_name,
                    "confidence": confidence,
                    "summary": ai_analysis.get("summary", ""),
                    "keywords": ai_analysis.get("keywords", []),
                    "rag_path": rag_path,
                    "original_path": file_path,
                    "destination": final_file_path 
                }

        # Low confidence - file stays in original location, but RAG is already created
        logger.warning(f"Low confidence: {confidence:.2%}")
        logger.info(f"File remains at: {file_path}")

        state.processing_stats["total"] += 1

        return {
            "status": "low_confidence",
            "file_name": Path(file_path).name,
            "confidence": confidence,
            "summary": ai_analysis.get("summary", ""),
            "suggestions": ai_analysis.get("category_suggestions", []),
            "rag_path": rag_path,
            "original_path": file_path,
            "destination": file_path 
        }

    except FileNotFoundError as e:
        logger.warning(f"File not found (may have been moved/deleted): {e}")
        state.processing_stats["total"] += 1

        return {
            "status": "skipped",
            "file_name": Path(file_path).name,
            "error": "File not found - may have already been processed",
        }

    except Exception as e:
        logger.error(f"Processing error: {e}", exc_info=True)
        import traceback

        traceback.print_exc()

        state.processing_stats["total"] += 1
        state.processing_stats["failed"] += 1

        return {"status": "error", "file_name": Path(file_path).name, "error": str(e)}
