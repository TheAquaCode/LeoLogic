"""
AI Tools - Exposes file organization functionality to the Chatbot
Smart Path Resolution + Action Execution
"""

import threading
import time
import os
from pathlib import Path
from .state import state
from .file_watcher import start_watching
from .file_processor import process_file
from .file_counter import count_files_in_folder
from utils.logger import setup_logger

logger = setup_logger(__name__)

def _resolve_path(path_str: str, allow_creation=False) -> str:
    """
    Smartly resolve paths from keywords.
    Prioritizes existing system folders (Pictures, Downloads) over creating new ones.
    """
    if not path_str: return None
    
    # Clean input: remove quotes, 'folder', 'my'
    clean_name = path_str.replace(" folder", "").replace("my ", "").strip().strip("'").strip('"')
    lower_input = clean_name.lower()
    
    # 1. Check absolute path
    path_obj = Path(clean_name)
    if path_obj.is_absolute() and path_obj.exists():
        return str(path_obj.resolve())

    # 2. Check Standard User Directories (The "Big 7")
    home = Path.home()
    
    # Check both standard and OneDrive variations
    candidates = [
        home / clean_name,              # C:/Users/Name/Input
        home / "OneDrive" / clean_name, # C:/Users/Name/OneDrive/Input
    ]

    # Map keywords to folder names
    key_map = {
        "download": "Downloads", "downloads": "Downloads",
        "doc": "Documents", "docs": "Documents", "document": "Documents", "documents": "Documents",
        "pic": "Pictures", "pics": "Pictures", "picture": "Pictures", "pictures": "Pictures",
        "vid": "Videos", "video": "Videos", "videos": "Videos",
        "mus": "Music", "music": "Music",
        "desk": "Desktop", "desktop": "Desktop"
    }

    # If input matches a keyword, add the proper casing to candidates
    for key, real_name in key_map.items():
        if key in lower_input:
            candidates.append(home / real_name)
            candidates.append(home / "OneDrive" / real_name)
            break

    # Check if any candidate exists
    for candidate in candidates:
        if candidate.exists():
            return str(candidate.resolve())

    # 3. Fuzzy Search in Roots (only if not found above)
    # This finds folders like "DesTest" if they live on Desktop or Documents
    search_roots = [
        home / "Desktop",
        home / "Documents",
        home / "OneDrive" / "Desktop",
        home / "OneDrive" / "Documents"
    ]
    
    for root in search_roots:
        if root.exists():
            try:
                potential = root / clean_name
                if potential.exists():
                    return str(potential.resolve())
            except: pass

    # 4. Creation / Fallback logic
    # If we are allowed to create (e.g., for Categories), default to User Home or Documents
    if allow_creation:
        # Default to C:/Users/Name/NewFolder
        target = home / clean_name
        return str(target.resolve())

    return None

def create_category(name: str, path: str):
    """Create a new organization category"""
    try:
        if not name: return "Error: Name is required."
        
        # Resolve path, allow creation because categories often point to new places
        final_path = _resolve_path(path, allow_creation=True) if path else _resolve_path(name, allow_creation=True)
        path_obj = Path(final_path)
        
        # Auto-create directory
        if not path_obj.exists():
            try:
                path_obj.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return f"Error: Could not create folder {final_path}: {e}"
        
        # Check duplicates
        if any(c['name'].lower() == name.lower() for c in state.categories):
            return f"Error: Category '{name}' already exists."

        new_category = {
            'id': len(state.categories) + 1,
            'name': name,
            'path': str(path_obj),
            'color': 'bg-blue-500',
            'rules': 0
        }
        
        state.categories.append(new_category)
        state.save_to_disk()
        return f"Success: Created category '{name}' -> {path_obj}"
    except Exception as e:
        return f"Error creating category: {str(e)}"

def add_watched_folder(path: str):
    """Start watching a folder"""
    try:
        if not path: return "Error: Path is required."
        
        # Do NOT allow creation for watched folders (you watch existing things)
        resolved_path = _resolve_path(path, allow_creation=False)
        
        if not resolved_path:
            return f"Error: Could not find folder '{path}'. I can only watch folders that already exist."

        path_obj = Path(resolved_path)

        # Check duplicates
        norm_new = os.path.normpath(str(path_obj)).lower()
        for f in state.watched_folders:
            norm_existing = os.path.normpath(f['path']).lower()
            if norm_existing == norm_new:
                return f"Info: Folder '{path_obj.name}' is already being watched."

        new_folder = {
            'id': len(state.watched_folders) + 1,
            'name': path_obj.name,
            'path': str(path_obj),
            'status': 'Active',
            'fileCount': count_files_in_folder(str(path_obj)),
            'lastActivity': 'Never',
            'last_activity_timestamp': 0
        }
        
        state.watched_folders.append(new_folder)
        state.save_to_disk()
        start_watching(new_folder['id'], new_folder['path'])
        
        return f"Success: Now watching '{path_obj.name}' ({str(path_obj)})"
    except Exception as e:
        return f"Error adding folder: {str(e)}"

def sort_folder(folder_name: str):
    """Trigger manual processing"""
    try:
        target = None
        # Try finding by name
        for f in state.watched_folders:
            if folder_name.lower() in f['name'].lower():
                target = f
                break
        
        if not target:
            return f"Error: Folder '{folder_name}' is not in the watched list."

        folder_id = target['id']
        folder_path = Path(target['path'])
        
        if not folder_path.exists():
            return "Error: Folder path not found on disk."

        files = [str(f) for f in folder_path.iterdir() if f.is_file()]
        if not files:
            return f"Folder '{target['name']}' is empty."

        state.processing_progress[folder_id] = {'total': len(files), 'completed': 0, 'failed': 0, 'in_progress': 0}

        def _process():
            for file_path in files:
                try:
                    res = process_file(file_path, folder_id)
                    if res.get('status') == 'success':
                        state.processing_progress[folder_id]['completed'] += 1
                    else:
                        state.processing_progress[folder_id]['failed'] += 1
                except:
                    state.processing_progress[folder_id]['failed'] += 1
            state.save_to_disk()

        threading.Thread(target=_process, daemon=True).start()
        
        return f"Started sorting {len(files)} files in '{target['name']}'."

    except Exception as e:
        return f"Error: {str(e)}"

def get_system_status():
    """Return simple context"""
    return {
        "watched_folders": [f['name'] for f in state.watched_folders],
        "categories": [c['name'] for c in state.categories]
    }