"""
File counting utility for watched folders
"""

import os
from pathlib import Path


def count_files_in_folder(folder_path: str) -> int:
    try:
        path = Path(folder_path)
        if not path.exists() or not path.is_dir():
            return 0
        count = 0
        for root, _, files in os.walk(path):
            count += len(files)
        return count
    except Exception:
        return 0
