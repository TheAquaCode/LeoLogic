"""
File counting utility for watched folders
"""

import os
from pathlib import Path


def count_files_in_folder(folder_path: str) -> int:
    """
    Count the number of files (not directories) in a folder and its subfolders
    
    Args:
        folder_path: Path to the folder to count files in
        
    Returns:
        int: Number of files found
    """
    try:
        path = Path(folder_path)
        if not path.exists() or not path.is_dir():
            return 0
            
        count = 0
        for root, _, files in os.walk(path):
            count += len(files)
        return count
    except Exception:
        return 0  # Return 0 if there's any error accessing the folder