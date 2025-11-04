"""
File Processing Pipeline with RAG Generation
"""

import shutil
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
    Complete file processing pipeline:
    1. Extract content (text, images, audio)
    2. Analyze with AI
    3. Classify into category
    4. Move to destination (if confident)
    5. Generate RAG document (using final path)
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

        # Step 3: Classify into category
        logger.debug("Classifying...")
        classification = AIProcessor.classify_into_categories(
            ai_analysis, state.categories
        )
        category_name = classification["category"]
        confidence = classification["confidence"]

        # Track the final file path (either moved or original)
        final_file_path = file_path

        # Check if we have a valid category
        if category_name and confidence >= CONFIDENCE_THRESHOLD:
            category = next(
                (c for c in state.categories if c["name"] == category_name), None
            )

            if category:
                # Step 4: Move file to destination FIRST
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

                # Step 5: Generate RAG document AFTER moving (using new path)
                logger.debug("Generating RAG document...")
                rag_path = RAGGenerator.create_rag_document(
                    final_file_path, extracted_data, ai_analysis, category_name
                )

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
                }

        # Low confidence - generate RAG with original path, don't move
        logger.warning(f"Low confidence: {confidence:.2%}")

        # Only create RAG if file still exists at original location
        if Path(final_file_path).exists():
            rag_path = RAGGenerator.create_rag_document(
                final_file_path, extracted_data, ai_analysis, "Uncategorized"
            )
        else:
            logger.warning(f"File moved/deleted before RAG creation: {final_file_path}")
            rag_path = None

        state.processing_stats["total"] += 1

        return {
            "status": "low_confidence",
            "file_name": Path(file_path).name,
            "confidence": confidence,
            "summary": ai_analysis.get("summary", ""),
            "suggestions": ai_analysis.get("category_suggestions", []),
            "rag_path": rag_path,
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
