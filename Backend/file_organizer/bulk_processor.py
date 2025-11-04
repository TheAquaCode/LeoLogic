"""
Bulk File Processor with Multi-threading
"""

import time
from pathlib import Path
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from config.settings import MAX_WORKERS
from .file_processor import process_file
from .state import state
from utils.logger import setup_logger
from utils.move_logger import save_session_report, start_new_session

logger = setup_logger(__name__)


class BulkProcessor:
    """Process multiple files with progress tracking"""
    
    def __init__(self):
        self.progress_lock = Lock()
        self.progress = {
            "total": 0,
            "completed": 0,
            "failed": 0,
            "in_progress": 0,
            "current_files": []
        }
    
    def process_files(self, file_paths: List[str], folder_id: int) -> Dict:
        """
        Process multiple files with multi-threading
        
        Args:
            file_paths: List of file paths to process
            folder_id: Folder ID for processing
            
        Returns:
            Dict with results and stats
        """
        start_time = time.time()
        start_new_session()  # Start new move tracking session
        
        with self.progress_lock:
            self.progress["total"] = len(file_paths)
            self.progress["completed"] = 0
            self.progress["failed"] = 0
            self.progress["in_progress"] = 0
            self.progress["current_files"] = []
        
        results = []
        
        logger.info(f"Starting bulk processing of {len(file_paths)} files with {MAX_WORKERS} workers")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit all files
            future_to_file = {
                executor.submit(self._process_single_file, file_path, folder_id): file_path
                for file_path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    with self.progress_lock:
                        if result.get("status") == "success":
                            self.progress["completed"] += 1
                        else:
                            self.progress["failed"] += 1
                        
                        # Remove from in-progress
                        if file_path in self.progress["current_files"]:
                            self.progress["current_files"].remove(file_path)
                        self.progress["in_progress"] = len(self.progress["current_files"])
                
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}", exc_info=True)
                    results.append({
                        "status": "error",
                        "file_name": Path(file_path).name,
                        "error": str(e)
                    })
                    
                    with self.progress_lock:
                        self.progress["failed"] += 1
        
        elapsed = time.time() - start_time
        
        # Generate move report
        report_path = save_session_report()
        
        logger.info(f"Bulk processing complete: {self.progress['completed']} succeeded, "
                   f"{self.progress['failed']} failed in {elapsed:.1f}s")
        
        return {
            "total": len(file_paths),
            "completed": self.progress["completed"],
            "failed": self.progress["failed"],
            "elapsed_time": elapsed,
            "results": results,
            "move_report": report_path
        }
    
    def _process_single_file(self, file_path: str, folder_id: int):
        """Process a single file with progress tracking"""
        with self.progress_lock:
            self.progress["in_progress"] += 1
            self.progress["current_files"].append(file_path)
        
        try:
            result = process_file(file_path, folder_id)
            return result
        finally:
            with self.progress_lock:
                self.progress["in_progress"] -= 1
                if file_path in self.progress["current_files"]:
                    self.progress["current_files"].remove(file_path)
    
    def get_progress(self) -> Dict:
        """Get current progress"""
        with self.progress_lock:
            return self.progress.copy()


# Global bulk processor instance
bulk_processor = BulkProcessor()
