"""
Enhanced AI Tools - PRODUCTION VERSION with comprehensive logging
All functions include detailed error handling and logging
"""

import threading
import time
import os
import json
from pathlib import Path
from typing import Dict, List, Optional

from .state import state
from .file_watcher import start_watching
from .file_processor import process_file
from .file_counter import count_files_in_folder
from utils.logger import setup_logger
from config.settings import RAG_DATA_DIR

logger = setup_logger(__name__)

# Pending confirmation tracker
pending_confirmations = {}


def _resolve_path(path_str: str, allow_creation=False) -> str:
    """
    Smartly resolve paths from keywords.
    Prioritizes existing system folders (Pictures, Downloads) over creating new ones.
    """
    if not path_str:
        return None

    # Clean input: remove quotes, 'folder', 'my'
    clean_name = (
        path_str.replace(" folder", "").replace("my ", "").strip().strip("'").strip('"')
    )
    lower_input = clean_name.lower()

    # 1. Check absolute path
    path_obj = Path(clean_name)
    if path_obj.is_absolute() and path_obj.exists():
        return str(path_obj.resolve())

    # 2. Check Standard User Directories (The "Big 7")
    home = Path.home()

    # Check both standard and OneDrive variations
    candidates = [
        home / clean_name,  # C:/Users/Name/Input
        home / "OneDrive" / clean_name,  # C:/Users/Name/OneDrive/Input
    ]

    # Map keywords to folder names
    key_map = {
        "download": "Downloads",
        "downloads": "Downloads",
        "doc": "Documents",
        "docs": "Documents",
        "document": "Documents",
        "documents": "Documents",
        "pic": "Pictures",
        "pics": "Pictures",
        "picture": "Pictures",
        "pictures": "Pictures",
        "vid": "Videos",
        "video": "Videos",
        "videos": "Videos",
        "mus": "Music",
        "music": "Music",
        "desk": "Desktop",
        "desktop": "Desktop",
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
    search_roots = [
        home / "Desktop",
        home / "Documents",
        home / "OneDrive" / "Desktop",
        home / "OneDrive" / "Documents",
    ]

    for root in search_roots:
        if root.exists():
            try:
                potential = root / clean_name
                if potential.exists():
                    return str(potential.resolve())
            except:
                pass

    # 4. Creation / Fallback logic
    if allow_creation:
        # Default to C:/Users/Name/NewFolder
        target = home / clean_name
        return str(target.resolve())

    return None


def create_category(name: str, path: str):
    """Create a new organization category"""
    try:
        logger.info(f"create_category called - name: '{name}', path: '{path}'")

        if not name:
            logger.warning("create_category: No name provided")
            return "Error: Category name is required."

        # Resolve path, allow creation because categories often point to new places
        final_path = (
            _resolve_path(path, allow_creation=True)
            if path
            else _resolve_path(name, allow_creation=True)
        )
        logger.info(f"Resolved category path: {final_path}")

        path_obj = Path(final_path)

        # Auto-create directory
        if not path_obj.exists():
            try:
                path_obj.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created category directory: {path_obj}")
            except Exception as e:
                logger.error(f"Failed to create category directory: {e}")
                return f"Error: Could not create folder {final_path}: {e}"

        # Check duplicates
        if any(c["name"].lower() == name.lower() for c in state.categories):
            logger.warning(f"Category '{name}' already exists")
            return f"Error: Category '{name}' already exists."

        new_category = {
            "id": len(state.categories) + 1,
            "name": name,
            "path": str(path_obj),
            "color": "bg-blue-500",
            "rules": 0,
        }

        state.categories.append(new_category)
        logger.info(
            f"Added category to state. Total categories: {len(state.categories)}"
        )

        try:
            state.save_to_disk()
            logger.info("State saved successfully")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            state.categories.remove(new_category)
            return f"Error: Could not save configuration: {str(e)}"

        return f"Success: Created category '{name}' at {path_obj}"

    except Exception as e:
        logger.error(f"Error in create_category: {e}", exc_info=True)
        return f"Error creating category: {str(e)}"


def create_folder(path: str, folder_name: str = None):
    """
    Create a new folder on the file system (not as a watched folder or category).
    This is for general folder creation requests.
    """
    try:
        logger.info(
            f"create_folder called - path: '{path}', folder_name: '{folder_name}'"
        )

        if not path:
            logger.warning("create_folder: No path provided")
            return "Error: Path is required."

        # If folder_name is provided, create it inside the path
        if folder_name:
            # Resolve the parent path
            parent_path = _resolve_path(path, allow_creation=True)
            if not parent_path:
                logger.error(f"Could not resolve parent path: {path}")
                return f"Error: Could not resolve path '{path}'."

            full_path = Path(parent_path) / folder_name
        else:
            # Just create the path itself
            full_path = Path(_resolve_path(path, allow_creation=True))

        logger.info(f"Target folder path: {full_path}")

        # Create the folder
        if full_path.exists():
            logger.info(f"Folder already exists: {full_path}")
            return f"Info: Folder already exists at {full_path}"

        try:
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Successfully created folder: {full_path}")
        except Exception as e:
            logger.error(f"Failed to create folder: {e}")
            return f"Error: Could not create folder: {str(e)}"

        return f"Success: Created folder at {full_path}"

    except Exception as e:
        logger.error(f"Error in create_folder: {e}", exc_info=True)
        return f"Error creating folder: {str(e)}"


def add_watched_folder(path: str):
    """Start watching a folder for automatic file organization"""
    try:
        logger.info(f"add_watched_folder called with path: {path}")

        if not path:
            return "Error: Path is required."

        # Do NOT allow creation for watched folders (you watch existing things)
        resolved_path = _resolve_path(path, allow_creation=False)
        logger.info(f"Resolved path: {resolved_path}")

        if not resolved_path:
            return f"Error: Could not find folder '{path}'. I can only watch folders that already exist."

        path_obj = Path(resolved_path)

        if not path_obj.exists():
            return f"Error: Path does not exist: {path_obj}"

        if not path_obj.is_dir():
            return f"Error: Path is not a directory: {path_obj}"

        # Check duplicates
        norm_new = os.path.normpath(str(path_obj)).lower()
        for f in state.watched_folders:
            norm_existing = os.path.normpath(f["path"]).lower()
            if norm_existing == norm_new:
                logger.info(f"Folder already watched: {path_obj.name}")
                return f"Info: Folder '{path_obj.name}' is already being watched."

        new_folder = {
            "id": len(state.watched_folders) + 1,
            "name": path_obj.name,
            "path": str(path_obj),
            "status": "Active",
            "fileCount": count_files_in_folder(str(path_obj)),
            "lastActivity": "Never",
            "last_activity_timestamp": 0,
        }

        logger.info(f"Created new folder entry: {new_folder}")

        # Add to state
        state.watched_folders.append(new_folder)
        logger.info(
            f"Added to state. Total watched folders: {len(state.watched_folders)}"
        )

        # Save to disk
        try:
            state.save_to_disk()
            logger.info("State saved to disk successfully")
        except Exception as e:
            logger.error(f"Failed to save state to disk: {e}")
            return f"Error: Could not save configuration: {str(e)}"

        # Start watching
        try:
            start_watching(new_folder["id"], new_folder["path"])
            logger.info(f"Started watching folder ID {new_folder['id']}")
        except Exception as e:
            logger.error(f"Failed to start watching: {e}")
            # Remove from state if watching failed
            state.watched_folders.remove(new_folder)
            state.save_to_disk()
            return f"Error: Could not start file watcher: {str(e)}"

        return f"Success: Now watching '{path_obj.name}' at {str(path_obj)}"

    except Exception as e:
        logger.error(f"Error in add_watched_folder: {e}", exc_info=True)
        return f"Error adding folder: {str(e)}"


def sort_folder(folder_name: str):
    """Trigger manual processing of a watched folder"""
    try:
        logger.info(f"sort_folder called with folder_name: '{folder_name}'")

        # Check if categories exist
        if not state.categories or len(state.categories) == 0:
            logger.warning("No categories configured - cannot organize files")
            return "Error: You need to create at least one category first. Categories are destination folders where your files will be organized. Try: 'Make a category called Work in Documents'"

        target = None

        # Try finding by name
        for f in state.watched_folders:
            if folder_name.lower() in f["name"].lower():
                target = f
                break

        if not target:
            logger.warning(f"Folder '{folder_name}' not in watched list")
            return f"Error: Folder '{folder_name}' is not in the watched list."

        logger.info(f"Found watched folder: {target['name']}")

        folder_id = target["id"]
        folder_path = Path(target["path"])

        if not folder_path.exists():
            logger.error(f"Folder path does not exist: {folder_path}")
            return "Error: Folder path not found on disk."

        files = [str(f) for f in folder_path.iterdir() if f.is_file()]
        logger.info(f"Found {len(files)} files to process")

        if not files:
            return f"Folder '{target['name']}' is empty."

        state.processing_progress[folder_id] = {
            "total": len(files),
            "completed": 0,
            "failed": 0,
            "in_progress": 0,
        }

        def _process():
            logger.info(f"Starting processing thread for {len(files)} files")
            for file_path in files:
                try:
                    res = process_file(file_path, folder_id)
                    if res.get("status") == "success":
                        state.processing_progress[folder_id]["completed"] += 1
                    else:
                        state.processing_progress[folder_id]["failed"] += 1
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    state.processing_progress[folder_id]["failed"] += 1
            state.save_to_disk()
            logger.info(
                f"Processing complete. Completed: {state.processing_progress[folder_id]['completed']}, Failed: {state.processing_progress[folder_id]['failed']}"
            )

        threading.Thread(target=_process, daemon=True).start()

        return f"Success: Started processing {len(files)} files in '{target['name']}'. Files will be organized into your categories: {', '.join([c['name'] for c in state.categories])}."

    except Exception as e:
        logger.error(f"Error in sort_folder: {e}", exc_info=True)
        return f"Error: {str(e)}"


def process_folder(path: str, confirmed: bool = False):
    """
    Process all files in a folder (even if not watched).
    For non-watched folders, requires confirmation.
    """
    try:
        logger.info(f"process_folder called - path: '{path}', confirmed: {confirmed}")

        # Check if categories exist
        if not state.categories or len(state.categories) == 0:
            logger.warning("No categories configured - cannot organize files")
            return "Error: You need to create at least one category first. Categories are destination folders where your files will be organized. Try: 'Make a category called Work in Documents'"

        if not path:
            return "Error: Path is required."

        # Resolve the path
        resolved_path = _resolve_path(path, allow_creation=False)
        logger.info(f"Resolved path: {resolved_path}")

        if not resolved_path:
            return f"Error: Could not find folder '{path}'."

        folder_path = Path(resolved_path)

        if not folder_path.exists():
            return f"Error: Folder does not exist: {folder_path}"

        if not folder_path.is_dir():
            return f"Error: Path is not a folder: {folder_path}"

        # Check if it's a watched folder
        is_watched = False
        watched_folder_id = None

        norm_target = os.path.normpath(str(folder_path)).lower()
        for f in state.watched_folders:
            norm_watched = os.path.normpath(f["path"]).lower()
            if norm_watched == norm_target:
                is_watched = True
                watched_folder_id = f["id"]
                break

        logger.info(f"Is watched folder: {is_watched}")

        # Count files
        files = [str(f) for f in folder_path.iterdir() if f.is_file()]
        file_count = len(files)
        logger.info(f"Found {file_count} files")

        if file_count == 0:
            return f"Folder '{folder_path.name}' is empty - no files to process."

        # If it's a watched folder, process immediately
        if is_watched:
            logger.info("Processing watched folder immediately")
            return _start_processing(
                folder_path, watched_folder_id, files, is_watched=True
            )

        # For non-watched folders, require confirmation
        if not confirmed:
            # Store the pending request
            confirmation_id = str(hash(str(folder_path)))
            pending_confirmations[confirmation_id] = {
                "path": str(folder_path),
                "files": files,
                "file_count": file_count,
            }

            logger.info(f"Confirmation required. ID: {confirmation_id}")

            category_list = ", ".join([c["name"] for c in state.categories])
            return f"CONFIRMATION_REQUIRED|{confirmation_id}|I found {file_count} files in:\n{folder_path}\n\nThis folder is not currently being watched. Files will be organized into your categories: {category_list}\n\nDo you want me to process all {file_count} files?"

        # User has confirmed, process the folder
        logger.info("Processing non-watched folder with confirmation")
        return _start_processing(folder_path, None, files, is_watched=False)

    except Exception as e:
        logger.error(f"Error in process_folder: {e}", exc_info=True)
        return f"Error processing folder: {str(e)}"


def confirm_process_folder(confirmation_id: str, confirmed: bool):
    """
    Confirm or cancel a pending folder processing request.
    """
    try:
        logger.info(
            f"confirm_process_folder called - ID: {confirmation_id}, confirmed: {confirmed}"
        )

        if confirmation_id not in pending_confirmations:
            logger.warning(f"Confirmation ID not found: {confirmation_id}")
            return "Error: No pending confirmation found. The request may have expired."

        if not confirmed:
            # User cancelled
            del pending_confirmations[confirmation_id]
            logger.info("User cancelled processing")
            return "Cancelled: Folder processing cancelled."

        # User confirmed, proceed with processing
        pending = pending_confirmations[confirmation_id]
        folder_path = Path(pending["path"])
        files = pending["files"]

        logger.info(f"User confirmed. Processing {len(files)} files from {folder_path}")

        # Clean up confirmation
        del pending_confirmations[confirmation_id]

        return _start_processing(folder_path, None, files, is_watched=False)

    except Exception as e:
        logger.error(f"Error in confirm_process_folder: {e}", exc_info=True)
        return f"Error confirming: {str(e)}"


def _start_processing(
    folder_path: Path, folder_id: Optional[int], files: List[str], is_watched: bool
):
    """
    Internal function to start processing files.
    """
    try:
        logger.info(
            f"_start_processing - folder: {folder_path}, is_watched: {is_watched}, files: {len(files)}"
        )

        # If not watched, create a temporary ID
        if folder_id is None:
            folder_id = f"temp_{hash(str(folder_path))}"
            logger.info(f"Created temp folder ID: {folder_id}")

        file_count = len(files)

        # Initialize progress tracking
        state.processing_progress[folder_id] = {
            "total": file_count,
            "completed": 0,
            "failed": 0,
            "in_progress": 0,
        }

        def _process():
            logger.info(f"Background processing started for {file_count} files")
            for file_path in files:
                try:
                    res = process_file(file_path, folder_id)
                    if res.get("status") == "success":
                        state.processing_progress[folder_id]["completed"] += 1
                    else:
                        state.processing_progress[folder_id]["failed"] += 1
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    state.processing_progress[folder_id]["failed"] += 1

            state.save_to_disk()
            logger.info(
                f"Background processing complete. Completed: {state.processing_progress[folder_id]['completed']}, Failed: {state.processing_progress[folder_id]['failed']}"
            )

        # Start processing in background thread
        threading.Thread(target=_process, daemon=True).start()

        folder_type = "watched folder" if is_watched else "folder"
        return f"Success: Started processing {file_count} files in {folder_type} '{folder_path.name}'."

    except Exception as e:
        logger.error(f"Error in _start_processing: {e}", exc_info=True)
        return f"Error starting processing: {str(e)}"


def search_rag_data(query: str, max_results: int = 5) -> str:
    """
    Search through RAG data to answer questions about processed files.
    Returns formatted context from RAG files.
    """
    try:
        logger.info(
            f"search_rag_data called - query: '{query}', max_results: {max_results}"
        )

        rag_dir = Path(RAG_DATA_DIR)

        if not rag_dir.exists():
            logger.warning("RAG directory does not exist")
            return "No RAG data available. Process some files first."

        results = []
        query_lower = query.lower()

        # Search through all RAG files
        rag_files = list(rag_dir.glob("*.rag.json"))
        logger.info(f"Searching through {len(rag_files)} RAG files")

        for rag_file in rag_files:
            try:
                with open(rag_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Search in summary and content
                summary = data.get("summary", "").lower()
                content = data.get("content", "").lower()
                file_name = data.get("original_file", rag_file.stem)

                # Simple keyword matching
                if any(
                    word in summary or word in content for word in query_lower.split()
                ):
                    results.append(
                        {
                            "file": file_name,
                            "summary": data.get("summary", "No summary")[:200],
                            "relevance": sum(
                                1
                                for word in query_lower.split()
                                if word in summary or word in content
                            ),
                        }
                    )

            except Exception as e:
                logger.error(f"Error reading RAG file {rag_file}: {e}")
                continue

        # Sort by relevance and limit
        results.sort(key=lambda x: x["relevance"], reverse=True)
        results = results[:max_results]

        logger.info(f"Found {len(results)} relevant results")

        if not results:
            return f"No files found matching '{query}'."

        # Format response
        response = f"Found {len(results)} relevant files:\n\n"
        for i, res in enumerate(results, 1):
            response += f"{i}. {res['file']}\n   {res['summary']}\n\n"

        return response

    except Exception as e:
        logger.error(f"Error in search_rag_data: {e}", exc_info=True)
        return f"Error searching RAG data: {str(e)}"


def get_file_layout(path: str = None, depth: int = 2) -> str:
    """
    Get the file/folder layout of a specified path or the user's home directory.
    Returns a tree-like structure of folders and files.
    """
    try:
        logger.info(f"get_file_layout called - path: '{path}', depth: {depth}")

        if path:
            resolved_path = _resolve_path(path, allow_creation=False)
            if not resolved_path:
                logger.error(f"Could not resolve path: {path}")
                return f"Error: Could not find path '{path}'."
            target_path = Path(resolved_path)
        else:
            target_path = Path.home()

        logger.info(f"Target path: {target_path}")

        if not target_path.exists():
            return f"Error: Path does not exist: {target_path}"

        def build_tree(
            current_path: Path, current_depth: int = 0, prefix: str = ""
        ) -> List[str]:
            """Recursively build a tree structure"""
            if current_depth > depth:
                return []

            lines = []
            try:
                items = sorted(
                    current_path.iterdir(),
                    key=lambda x: (not x.is_dir(), x.name.lower()),
                )

                # Filter out hidden files and common ignore patterns
                items = [
                    item
                    for item in items
                    if not item.name.startswith(".")
                    and item.name not in ["node_modules", "__pycache__", "venv", ".git"]
                ]

                for i, item in enumerate(items):
                    is_last = i == len(items) - 1
                    connector = "└── " if is_last else "├── "

                    # Add file size for files
                    if item.is_file():
                        size = item.stat().st_size
                        size_str = f" ({_format_size(size)})"
                        lines.append(f"{prefix}{connector}{item.name}{size_str}")
                    else:
                        lines.append(f"{prefix}{connector}{item.name}/")

                        # Recurse into directories
                        if current_depth < depth:
                            extension = "    " if is_last else "│   "
                            lines.extend(
                                build_tree(item, current_depth + 1, prefix + extension)
                            )

            except PermissionError:
                lines.append(f"{prefix}└── [Permission Denied]")

            return lines

        tree_lines = [str(target_path) + "/"]
        tree_lines.extend(build_tree(target_path))

        result = "\n".join(tree_lines)
        logger.info(f"Generated file layout with {len(tree_lines)} lines")

        return result

    except Exception as e:
        logger.error(f"Error in get_file_layout: {e}", exc_info=True)
        return f"Error getting file layout: {str(e)}"


def _format_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def list_categories() -> str:
    """List all current categories"""
    try:
        logger.info("list_categories called")

        if not state.categories:
            logger.info("No categories configured")
            return "No categories configured yet."

        result = "Current categories:\n"
        for cat in state.categories:
            result += f"  • {cat['name']} → {cat['path']}\n"

        logger.info(f"Listed {len(state.categories)} categories")
        return result

    except Exception as e:
        logger.error(f"Error in list_categories: {e}", exc_info=True)
        return f"Error listing categories: {str(e)}"


def list_watched_folders() -> str:
    """List all watched folders"""
    try:
        logger.info("list_watched_folders called")

        if not state.watched_folders:
            logger.info("No watched folders configured")
            return "No folders being watched yet."

        result = "Watched folders:\n"
        for folder in state.watched_folders:
            status = folder.get("status", "Unknown")
            file_count = folder.get("fileCount", 0)
            result += f"  • {folder['name']} ({status}) - {file_count} files\n    Path: {folder['path']}\n"

        logger.info(f"Listed {len(state.watched_folders)} watched folders")
        return result

    except Exception as e:
        logger.error(f"Error in list_watched_folders: {e}", exc_info=True)
        return f"Error listing watched folders: {str(e)}"


def get_system_status():
    """Return comprehensive system status"""
    try:
        logger.info("get_system_status called")

        status = {
            "watched_folders": [f["name"] for f in state.watched_folders],
            "watched_folder_details": state.watched_folders,
            "categories": [c["name"] for c in state.categories],
            "category_details": state.categories,
            "total_watched": len(state.watched_folders),
            "total_categories": len(state.categories),
        }

        logger.info(
            f"System status: {status['total_watched']} watched folders, {status['total_categories']} categories"
        )
        return status

    except Exception as e:
        logger.error(f"Error in get_system_status: {e}", exc_info=True)
        return {
            "watched_folders": [],
            "watched_folder_details": [],
            "categories": [],
            "category_details": [],
            "total_watched": 0,
            "total_categories": 0,
        }


# Tool registry for easy lookup
AVAILABLE_TOOLS = {
    "create_category": {
        "function": create_category,
        "description": "Creates a destination category for organizing files",
        "params": ["name", "path"],
    },
    "create_folder": {
        "function": create_folder,
        "description": "Creates a new folder on the file system",
        "params": ["path", "folder_name"],
    },
    "add_watched_folder": {
        "function": add_watched_folder,
        "description": "Adds a source folder to monitor for file organization",
        "params": ["path"],
    },
    "sort_folder": {
        "function": sort_folder,
        "description": "Manually triggers sorting for a watched folder",
        "params": ["folder_name"],
    },
    "process_folder": {
        "function": process_folder,
        "description": "Process all files in any folder (watched or not, requires confirmation for non-watched)",
        "params": ["path", "confirmed"],
    },
    "confirm_process_folder": {
        "function": confirm_process_folder,
        "description": "Confirm or cancel a pending folder processing request",
        "params": ["confirmation_id", "confirmed"],
    },
    "search_rag": {
        "function": search_rag_data,
        "description": "Searches through processed file data to answer questions",
        "params": ["query", "max_results"],
    },
    "get_file_layout": {
        "function": get_file_layout,
        "description": "Shows the folder/file structure at a given path",
        "params": ["path", "depth"],
    },
    "list_categories": {
        "function": list_categories,
        "description": "Lists all configured categories",
        "params": [],
    },
    "list_watched_folders": {
        "function": list_watched_folders,
        "description": "Lists all watched folders",
        "params": [],
    },
}
