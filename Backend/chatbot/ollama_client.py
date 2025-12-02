"""
Enhanced Ollama Chatbot with RAG Integration & Comprehensive Tool Use
Supports: Categories, Folders, Watched Folders, RAG Search, File Layout Queries
"""

import ollama
import requests
import sys
import re
import json
from typing import Dict, Any, Optional

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from utils.logger import setup_logger
from file_organizer import tools  # This imports your enhanced tools

logger = setup_logger(__name__)

from config.settings import (
    OLLAMA_HOST,
    PHI3_MODEL,
    MAX_CONVERSATION_HISTORY,
    ENABLE_RAG,
    FILE_ORGANIZER_PORT,
)


class OllamaChatbot:
    def __init__(self):
        self.client = ollama.Client(host=OLLAMA_HOST)
        self.conversation_history = []
        self.is_ready = True
        self.loading = False

    def _get_system_instruction(self):
        """Enhanced System Prompt with all available tools"""
        status = tools.get_system_status()

        return f"""You are Clanky, an automated File Organizer assistant.

Current Configuration:
- Categories: {', '.join(status['categories']) if status['categories'] else 'None'}
- Watched Folders: {', '.join(status['watched_folders']) if status['watched_folders'] else 'None'}

AVAILABLE TOOLS:

1. create_category(name, path)
   - Creates a DESTINATION category where files will be organized
   - Example: {{"tool": "create_category", "args": {{"name": "Work Docs", "path": "Documents/Work"}}}}

2. create_folder(path, folder_name)
   - Creates a regular folder on the file system (not for organizing)
   - Example: {{"tool": "create_folder", "args": {{"path": "Desktop", "folder_name": "New Project"}}}}

3. add_watched_folder(path)
   - Adds a SOURCE folder to monitor for automatic file organization
   - Example: {{"tool": "add_watched_folder", "args": {{"path": "Downloads"}}}}

4. sort_folder(folder_name)
   - Manually triggers file sorting for a watched folder
   - Example: {{"tool": "sort_folder", "args": {{"folder_name": "Downloads"}}}}

5. search_rag(query, max_results)
   - Searches processed file data to answer questions about files
   - Example: {{"tool": "search_rag", "args": {{"query": "contract documents", "max_results": 5}}}}

6. get_file_layout(path, depth)
   - Shows folder/file structure at a location
   - Example: {{"tool": "get_file_layout", "args": {{"path": "Documents", "depth": 2}}}}

7. list_categories()
   - Lists all configured categories
   - Example: {{"tool": "list_categories", "args": {{}}}}

8. list_watched_folders()
   - Lists all watched folders with their status
   - Example: {{"tool": "list_watched_folders", "args": {{}}}}

INSTRUCTIONS:
- When the user asks to perform an action, return ONLY a JSON object
- Format: {{"tool": "tool_name", "args": {{"arg1": "value", "arg2": "value"}}}}
- Do NOT wrap in markdown code blocks (no ```json)
- If NO action is needed (just answering questions), reply with normal conversational text
- Use create_category for organizing destinations
- Use add_watched_folder for monitoring source folders
- Use create_folder for general folder creation
- When user asks about files or documents, use search_rag
- When user asks about folder structure, use get_file_layout

EXAMPLES:
User: "Make a category called Photos in my Pictures folder"
Response: {{"tool": "create_category", "args": {{"name": "Photos", "path": "Pictures"}}}}

User: "Watch my Downloads folder"
Response: {{"tool": "add_watched_folder", "args": {{"path": "Downloads"}}}}

User: "Create a folder called Projects on my Desktop"
Response: {{"tool": "create_folder", "args": {{"path": "Desktop", "folder_name": "Projects"}}}}

User: "What files do I have about taxes?"
Response: {{"tool": "search_rag", "args": {{"query": "taxes", "max_results": 5}}}}

User: "Show me what's in my Documents folder"
Response: {{"tool": "get_file_layout", "args": {{"path": "Documents", "depth": 2}}}}

User: "What categories do I have?"
Response: {{"tool": "list_categories", "args": {{}}}}
"""

    def search_files(self, query: str) -> Optional[str]:
        """Search through RAG data via the file organizer API"""
        try:
            response = requests.post(
                f"http://localhost:{FILE_ORGANIZER_PORT}/api/rag/search",
                json={"query": query, "max_results": 3},
                timeout=3,
            )

            if response.status_code == 200:
                results = response.json().get("results", [])
                if not results:
                    return None

                context = f"Search Results:\n"
                for res in results:
                    context += f"- {res['file']}: {res.get('summary', '')[:100]}...\n"

                return context
        except:
            return None

        return None

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Execute the specified tool with arguments"""
        try:
            logger.info(f"🔧 Tool Exec: {tool_name} {args}")

            # Use the tools module which has all the functions
            if tool_name == "create_category":
                return tools.create_category(args.get("name"), args.get("path"))

            elif tool_name == "create_folder":
                return tools.create_folder(args.get("path"), args.get("folder_name"))

            elif tool_name == "add_watched_folder":
                return tools.add_watched_folder(args.get("path"))

            elif tool_name == "sort_folder":
                return tools.sort_folder(args.get("folder_name"))

            elif tool_name == "search_rag":
                return tools.search_rag_data(
                    args.get("query", ""), args.get("max_results", 5)
                )

            elif tool_name == "get_file_layout":
                return tools.get_file_layout(args.get("path"), args.get("depth", 2))

            elif tool_name == "list_categories":
                return tools.list_categories()

            elif tool_name == "list_watched_folders":
                return tools.list_watched_folders()

            else:
                return f"Error: Unknown tool '{tool_name}'"

        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return f"Tool Error: {str(e)}"

    def _detect_intent(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Detect user intent and suggest tool usage for better accuracy.
        This helps catch commands even if AI doesn't output perfect JSON.
        """
        message_lower = message.lower()

        # Category creation patterns
        if any(
            word in message_lower
            for word in [
                "make category",
                "create category",
                "add category",
                "new category",
            ]
        ):
            return {"intent": "create_category", "confidence": "high"}

        # Folder creation patterns
        if any(
            word in message_lower
            for word in ["make folder", "create folder", "new folder", "make a folder"]
        ):
            # Distinguish from "watch folder"
            if "watch" not in message_lower and "monitor" not in message_lower:
                return {"intent": "create_folder", "confidence": "high"}

        # Watched folder patterns
        if any(
            word in message_lower
            for word in ["watch", "monitor", "track folder", "add watched"]
        ):
            return {"intent": "add_watched_folder", "confidence": "high"}

        # Sort/process patterns
        if any(
            word in message_lower
            for word in ["sort", "organize", "process files", "clean up"]
        ):
            return {"intent": "sort_folder", "confidence": "medium"}

        # Search patterns
        if any(
            word in message_lower
            for word in [
                "find file",
                "search for",
                "look for",
                "files about",
                "documents about",
            ]
        ):
            return {"intent": "search_rag", "confidence": "high"}

        # File layout patterns
        if any(
            word in message_lower
            for word in [
                "show me",
                "what's in",
                "list files",
                "folder structure",
                "directory",
            ]
        ):
            return {"intent": "get_file_layout", "confidence": "medium"}

        # List patterns
        if (
            "list categories" in message_lower
            or "show categories" in message_lower
            or "what categories" in message_lower
        ):
            return {"intent": "list_categories", "confidence": "high"}

        if (
            "list watched" in message_lower
            or "show watched" in message_lower
            or "what folders are" in message_lower
        ):
            return {"intent": "list_watched_folders", "confidence": "high"}

        return None

    def generate_response(self, user_message: str) -> str:
        try:
            # Build message context
            messages = [{"role": "system", "content": self._get_system_instruction()}]

            # Add limited conversation history
            for msg in self.conversation_history[-2:]:
                messages.append({"role": "user", "content": msg["user"]})
                messages.append({"role": "assistant", "content": msg["assistant"]})

            # Check if RAG search might be useful
            if ENABLE_RAG and any(
                word in user_message.lower()
                for word in ["find", "search", "file", "document"]
            ):
                rag = self.search_files(user_message)
                if rag:
                    messages.append({"role": "system", "content": rag})

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Get AI response
            response = self.client.chat(model=PHI3_MODEL, messages=messages)
            ai_text = response["message"]["content"].strip()

            # Clean up potential markdown wrappers
            clean_text = re.sub(r"```json\s*", "", ai_text)
            clean_text = re.sub(r"```", "", clean_text).strip()

            # Try to detect JSON command
            json_match = re.search(r"\{.*\}", clean_text, re.DOTALL)

            if json_match:
                try:
                    command_data = json.loads(json_match.group(0))
                    tool_name = command_data.get("tool")
                    args = command_data.get("args", {})

                    if tool_name:
                        # Execute the tool
                        result = self.execute_tool(tool_name, args)

                        # Generate a natural language summary
                        confirm_msgs = [
                            {
                                "role": "system",
                                "content": "You are a helpful assistant. Provide a brief, friendly confirmation based on the SYSTEM OUTPUT. Be natural and concise.",
                            },
                            {
                                "role": "user",
                                "content": f"User Request: {user_message}\n\nSYSTEM OUTPUT: {result}\n\nProvide a natural, one-sentence confirmation.",
                            },
                        ]

                        final_resp = self.client.chat(
                            model=PHI3_MODEL, messages=confirm_msgs
                        )
                        final_text = final_resp["message"]["content"]

                        # Save to history
                        self.conversation_history.append(
                            {"user": user_message, "assistant": final_text}
                        )

                        return final_text

                except json.JSONDecodeError:
                    pass

            # Fallback: Intent detection for robustness
            intent = self._detect_intent(user_message)
            if intent and intent["confidence"] == "high":
                # Could implement fallback tool execution here if desired
                pass

            # No tool execution needed - just conversational response
            self.conversation_history.append(
                {"user": user_message, "assistant": ai_text}
            )

            return ai_text

        except Exception as e:
            logger.error(f"Chat Error: {e}")
            return "I'm having trouble processing that right now. Please check the backend logs for details."

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
