import ollama
import sys
import re
from typing import Optional, Dict, Tuple

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from utils.logger import setup_logger
from file_organizer import tools
from config.settings import OLLAMA_HOST, PHI3_MODEL

logger = setup_logger(__name__)


class OllamaChatbot:
    def __init__(self):
        self.client = ollama.Client(host=OLLAMA_HOST)
        self.conversation_history = []
        self.pending_confirmation = None
        self.is_ready = True
        self.loading = False

    def _parse_user_intent(self, message: str) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Parse user message and extract tool + parameters
        Returns: (tool_name, args) or (None, None)
        """
        msg_lower = message.lower()

        # ORGANIZE/PROCESS FOLDER
        if any(
            word in msg_lower
            for word in [
                "organize",
                "organise",
                "process",
                "sort",
                "start organizing",
                "start processing",
            ]
        ):
            # Extract full path with pattern matching
            # Pattern 1: Full Windows path (C:\...\...)
            path_match = re.search(r"[A-Z]:[\\\/][^\s,;]+", message, re.IGNORECASE)
            if path_match:
                path = path_match.group(0).strip()
                logger.info(f"[ORGANIZE] {path}")
                return ("process_folder", {"path": path, "confirmed": False})

            # Pattern 2: Keyword path (organize Downloads, organize Desktop)
            for keyword in ["downloads", "desktop", "documents", "pictures", "videos"]:
                if keyword in msg_lower:
                    path = keyword.capitalize()
                    logger.info(f"[ORGANIZE] {path}")
                    return ("process_folder", {"path": path, "confirmed": False})

        # CREATE FOLDER
        if (
            any(word in msg_lower for word in ["create", "make"])
            and "folder" in msg_lower
        ):
            # Extract folder name from "called X" or "named X"
            name_match = re.search(
                r'(?:called|named)\s+["\']?([^"\']+?)["\']?(?:\s+on|\s+in|\s|$)',
                message,
                re.IGNORECASE,
            )
            if name_match:
                folder_name = name_match.group(1).strip()
                # Determine location
                location = "Desktop"  # default
                if "documents" in msg_lower:
                    location = "Documents"
                elif "downloads" in msg_lower:
                    location = "Downloads"

                logger.info(f"[CREATE FOLDER] {folder_name} in {location}")
                return ("create_folder", {"path": location, "folder_name": folder_name})

        # WATCH FOLDER
        if any(word in msg_lower for word in ["watch", "monitor"]):
            # Full path
            path_match = re.search(r"[A-Z]:[\\\/][^\s,;]+", message, re.IGNORECASE)
            if path_match:
                path = path_match.group(0).strip()
                logger.info(f"[WATCH] {path}")
                return ("add_watched_folder", {"path": path})

            # Keyword path
            for keyword in ["downloads", "desktop", "documents", "pictures"]:
                if keyword in msg_lower:
                    path = keyword.capitalize()
                    logger.info(f"[WATCH] {path}")
                    return ("add_watched_folder", {"path": path})

        # CREATE CATEGORY
        if (
            any(word in msg_lower for word in ["create", "make", "add"])
            and "category" in msg_lower
        ):
            name_match = re.search(
                r'(?:called|named)\s+["\']?([^"\']+?)["\']?(?:\s+in|\s+at|\s|$)',
                message,
                re.IGNORECASE,
            )
            if name_match:
                cat_name = name_match.group(1).strip()
                # Determine destination
                dest = "Documents"  # default
                if "pictures" in msg_lower:
                    dest = "Pictures"
                elif "desktop" in msg_lower:
                    dest = "Desktop"

                logger.info(f"[CREATE CATEGORY] {cat_name} in {dest}")
                return ("create_category", {"name": cat_name, "path": dest})

        # SHOW/LIST FILES
        if any(word in msg_lower for word in ["what's", "show", "list", "what"]):
            if "desktop" in msg_lower:
                logger.info(f"[SHOW] Desktop")
                return ("get_file_layout", {"path": "Desktop", "depth": 1})
            elif "documents" in msg_lower:
                logger.info(f"[SHOW] Documents")
                return ("get_file_layout", {"path": "Documents", "depth": 1})
            elif "downloads" in msg_lower:
                logger.info(f"[SHOW] Downloads")
                return ("get_file_layout", {"path": "Downloads", "depth": 1})

        # LIST CATEGORIES
        if "categories" in msg_lower and any(
            word in msg_lower for word in ["show", "list", "what"]
        ):
            logger.info(f"[LIST CATEGORIES]")
            return ("list_categories", {})

        # LIST WATCHED
        if "watched" in msg_lower and any(
            word in msg_lower for word in ["show", "list", "what"]
        ):
            logger.info(f"[LIST WATCHED]")
            return ("list_watched_folders", {})

        # SEARCH FILES (RAG - search through processed file content)
        if any(
            word in msg_lower
            for word in [
                "find",
                "search",
                "do i have",
                "where is",
                "locate",
                "look for",
            ]
        ):
            # Extract search query
            query = None

            # Pattern: "find my X"
            match = re.search(
                r"(?:find|search|locate|look for)\s+(?:my\s+)?(.+)",
                message,
                re.IGNORECASE,
            )
            if match:
                query = match.group(1).strip()

            # Pattern: "do i have any X"
            if not query:
                match = re.search(
                    r"do i have\s+(?:any\s+)?(.+)", message, re.IGNORECASE
                )
                if match:
                    query = match.group(1).strip()

            # Pattern: "where is my X"
            if not query:
                match = re.search(
                    r"where (?:is|are)\s+(?:my\s+)?(.+)", message, re.IGNORECASE
                )
                if match:
                    query = match.group(1).strip()

            if query:
                # Remove trailing punctuation
                query = query.rstrip("?!.,")
                logger.info(f"[SEARCH RAG] {query}")
                return ("search_rag", {"query": query, "max_results": 5})

        # No tool detected - it's chat
        logger.info("[CHAT MODE]")
        return (None, None)

    def _execute_tool(self, tool_name: str, args: Dict) -> str:
        """Execute a tool and return result"""
        try:
            logger.info(f"[EXECUTING] {tool_name}")
            logger.info(f"[ARGS] {args}")

            # Execute the appropriate tool
            if tool_name == "process_folder":
                result = tools.process_folder(
                    args.get("path"), args.get("confirmed", False)
                )
            elif tool_name == "create_folder":
                result = tools.create_folder(args.get("path"), args.get("folder_name"))
            elif tool_name == "add_watched_folder":
                result = tools.add_watched_folder(args.get("path"))
            elif tool_name == "create_category":
                result = tools.create_category(args.get("name"), args.get("path"))
            elif tool_name == "get_file_layout":
                result = tools.get_file_layout(args.get("path"), args.get("depth", 2))
            elif tool_name == "list_categories":
                result = tools.list_categories()
            elif tool_name == "list_watched_folders":
                result = tools.list_watched_folders()
            elif tool_name == "search_rag":
                result = tools.search_rag_data(
                    args.get("query"), args.get("max_results", 5)
                )
            else:
                result = f"Error: Unknown tool {tool_name}"

            logger.info(f"[RESULT] {result[:100]}...")
            return result

        except Exception as e:
            logger.error(f"[TOOL ERROR] {e}", exc_info=True)
            return f"Error: {str(e)}"

    def generate_response(self, user_message: str) -> str:
        """Main response generator"""
        try:
            logger.info(f"[USER] {user_message}")

            # Handle pending confirmation
            if self.pending_confirmation:
                return self._handle_confirmation(user_message)

            # Parse user intent
            tool_name, args = self._parse_user_intent(user_message)

            # If tool detected, execute it
            if tool_name:
                result = self._execute_tool(tool_name, args)

                # Handle confirmation request
                if result.startswith("CONFIRMATION_REQUIRED|"):
                    return self._handle_confirmation_request(result, user_message)

                # For file layout, return directly
                if tool_name == "get_file_layout":
                    self.conversation_history.append(
                        {"user": user_message, "assistant": result}
                    )
                    return result

                # For RAG search, return directly (already formatted nicely)
                if tool_name == "search_rag":
                    self.conversation_history.append(
                        {"user": user_message, "assistant": result}
                    )
                    return result

                # For other tools, clean up the response
                if result.startswith("Success:"):
                    response = result.replace("Success: ", "")
                elif result.startswith("Error:"):
                    response = result
                elif result.startswith("Info:"):
                    response = result.replace("Info: ", "")
                else:
                    response = result

                self.conversation_history.append(
                    {"user": user_message, "assistant": response}
                )
                return response

            # No tool - chat with AI
            return self._chat_response(user_message)

        except Exception as e:
            logger.error(f"[ERROR] {e}", exc_info=True)
            return "I'm having trouble with that request. Please check the logs."

    def _chat_response(self, user_message: str) -> str:
        """Generate conversational response"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are Clanky, a helpful file organization assistant. Be friendly and conversational. Keep responses brief.",
                }
            ]

            # Add recent history
            for msg in self.conversation_history[-2:]:
                messages.append({"role": "user", "content": msg["user"]})
                messages.append({"role": "assistant", "content": msg["assistant"]})

            messages.append({"role": "user", "content": user_message})

            response = self.client.chat(model=PHI3_MODEL, messages=messages)
            ai_response = response["message"]["content"].strip()

            self.conversation_history.append(
                {"user": user_message, "assistant": ai_response}
            )
            return ai_response

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return "I'm here to help! What would you like to do?"

    def _handle_confirmation_request(self, result: str, user_message: str) -> str:
        """Handle confirmation request from process_folder"""
        parts = result.split("|", 2)
        confirmation_id = parts[1]
        message = parts[2]

        self.pending_confirmation = {
            "id": confirmation_id,
            "original_message": user_message,
        }

        # Parse the message to extract info
        try:
            file_count_match = re.search(r"(\d+)\s+files?", message)
            path_match = re.search(r"in:\s*\n\s*(.+?)\s*\n", message, re.MULTILINE)

            file_count = file_count_match.group(1) if file_count_match else "some"
            path = path_match.group(1).strip() if path_match else "that folder"

            response = f"I'd like to organize:\n{path}\n\nI found {file_count} files.\n\nReply 'yes' or 'no'."
        except:
            response = f"{message}\n\nReply 'yes' or 'no'."

        self.conversation_history.append({"user": user_message, "assistant": response})
        return response

    def _handle_confirmation(self, user_message: str) -> str:
        """Handle yes/no confirmation"""
        msg_lower = user_message.lower().strip()

        # Check response
        if any(
            word in msg_lower
            for word in ["yes", "y", "yeah", "yep", "sure", "ok", "okay"]
        ):
            confirmed = True
        elif any(word in msg_lower for word in ["no", "n", "nope", "cancel", "stop"]):
            confirmed = False
        else:
            return "Please reply 'yes' or 'no'."

        # Execute confirmation
        confirmation_id = self.pending_confirmation["id"]
        self.pending_confirmation = None

        result = tools.confirm_process_folder(confirmation_id, confirmed)

        if confirmed:
            response = "Great! " + result.replace("Success: ", "")
        else:
            response = result.replace("Cancelled: ", "")

        self.conversation_history.append({"user": user_message, "assistant": response})
        return response

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.pending_confirmation = None
        logger.info("[HISTORY CLEARED]")
