"""
Enhanced Ollama Chatbot with Smart RAG Detection and Confirmation Handling
Supports folder processing with user confirmation for non-watched folders
"""

import ollama
import requests
import sys
import re
import json
from typing import Dict, Any, Optional

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from utils.logger import setup_logger
from file_organizer import tools

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
        self.pending_confirmation = None  # Tracks confirmation requests

    def _get_system_instruction(self):
        """Enhanced System Prompt with process_folder and smart tool selection"""
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
   - Creates a regular folder on the file system
   - Example: {{"tool": "create_folder", "args": {{"path": "Desktop", "folder_name": "New Project"}}}}

3. add_watched_folder(path)
   - Adds a SOURCE folder to monitor for automatic file organization
   - Example: {{"tool": "add_watched_folder", "args": {{"path": "Downloads"}}}}

4. sort_folder(folder_name)
   - Manually triggers file sorting for a watched folder (watched folders only)
   - Example: {{"tool": "sort_folder", "args": {{"folder_name": "Downloads"}}}}

5. process_folder(path, confirmed)
   - Process ALL files in ANY folder (even if not watched)
   - Use when user says "process files in", "organize", "sort all files"
   - Example: {{"tool": "process_folder", "args": {{"path": "Desktop/Screenshots", "confirmed": false}}}}

6. search_rag(query, max_results)
   - Searches PROCESSED FILE CONTENT to answer questions about specific files/documents
   - Use ONLY when user asks about FILE CONTENT (documents, reports, invoices, etc.)
   - Example: {{"tool": "search_rag", "args": {{"query": "tax documents", "max_results": 5}}}}

7. get_file_layout(path, depth)
   - Shows the ACTUAL folder/file structure at a location
   - Use when user asks "what's in", "show me", "list files/folders", "what folders do I have"
   - Example: {{"tool": "get_file_layout", "args": {{"path": "Desktop", "depth": 2}}}}

8. list_categories()
   - Lists all configured categories
   - Example: {{"tool": "list_categories", "args": {{}}}}

9. list_watched_folders()
   - Lists all watched folders with their status
   - Example: {{"tool": "list_watched_folders", "args": {{}}}}

CRITICAL DISTINCTIONS:

**Use get_file_layout() when user asks:**
- "What folders are on my Desktop?"
- "Show me what's in my Documents"
- "List the files in Downloads"
- "What do I have in Pictures?"
- "What's on my Desktop?"
- ANY question about folder/file structure or "what's in" a location

**Use search_rag() when user asks:**
- "Find my tax returns"
- "Do I have any invoices?"
- "Show me documents about contracts"
- "Find files related to work projects"
- ANY question about FILE CONTENT or searching for specific documents

**Use process_folder() when user asks:**
- "Process all files in Desktop"
- "Organize everything in Downloads"
- "Sort all files in Screenshots folder"
- "Clean up my Documents folder"
- ANY request to process/organize/sort files in a specific location

INSTRUCTIONS:
- When user asks about folder contents/structure → ALWAYS use get_file_layout()
- When user asks about finding specific files by content → use search_rag()
- When user asks to process/organize/sort a folder → use process_folder()
- Return ONLY JSON for actions: {{"tool": "tool_name", "args": {{"arg1": "value"}}}}
- Do NOT wrap in markdown code blocks (no ```json)
- For normal conversation, reply with text (no JSON)

EXAMPLES:

User: "Process all files in my Desktop"
Response: {{"tool": "process_folder", "args": {{"path": "Desktop", "confirmed": false}}}}

User: "Organize everything in Downloads"
Response: {{"tool": "process_folder", "args": {{"path": "Downloads", "confirmed": false}}}}

User: "What folders do I have on my Desktop?"
Response: {{"tool": "get_file_layout", "args": {{"path": "Desktop", "depth": 1}}}}

User: "Find my tax returns"
Response: {{"tool": "search_rag", "args": {{"query": "tax returns", "max_results": 5}}}}
"""

    def _detect_query_type(self, message: str) -> str:
        """
        Detect if user is asking about:
        - 'layout': Folder structure / what's in a location
        - 'content': Searching for specific file content
        - 'process': Process/organize files in a folder
        - 'action': Wants to perform an action
        - 'chat': Just conversational
        """
        message_lower = message.lower()

        # Process queries - asking to organize/process files
        process_keywords = [
            "process",
            "organize",
            "sort",
            "clean up",
            "process all",
            "organize all",
            "sort all",
            "process files",
            "organize files",
            "sort files",
            "process everything",
            "organize everything",
        ]

        # Layout queries - asking about folder structure
        layout_keywords = [
            "what folders",
            "what files",
            "what's in",
            "what is in",
            "show me",
            "list files",
            "list folders",
            "what do i have in",
            "what's on",
            "what is on",
            "contents of",
            "in my desktop",
            "on my desktop",
            "folders on",
            "files on",
            "folders in",
            "files in",
        ]

        # Content queries - searching for specific documents
        content_keywords = [
            "find",
            "search",
            "look for",
            "do i have any",
            "where is my",
            "locate",
            "documents about",
            "files about",
            "invoices",
            "contracts",
            "reports",
            "receipts",
            "tax",
            "returns",
        ]

        # Check for process queries first (highest priority for this feature)
        if any(keyword in message_lower for keyword in process_keywords):
            return "process"

        # Check for layout queries
        if any(keyword in message_lower for keyword in layout_keywords):
            return "layout"

        # Check for content queries
        if any(keyword in message_lower for keyword in content_keywords):
            return "content"

        # Check for action queries
        action_keywords = ["create", "make", "add", "watch", "monitor"]
        if any(keyword in message_lower for keyword in action_keywords):
            return "action"

        return "chat"

    def _inject_context_hint(self, message: str, query_type: str) -> str:
        """Add a hint to the message to guide the AI"""
        if query_type == "process":
            return f"{message}\n\n[SYSTEM HINT: User wants to process/organize files in a folder. Use process_folder tool.]"
        elif query_type == "layout":
            return f"{message}\n\n[SYSTEM HINT: User is asking about folder structure. Use get_file_layout tool.]"
        elif query_type == "content":
            return f"{message}\n\n[SYSTEM HINT: User is searching for specific file content. Use search_rag tool.]"
        return message

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

            if tool_name == "create_category":
                return tools.create_category(args.get("name"), args.get("path"))

            elif tool_name == "create_folder":
                return tools.create_folder(args.get("path"), args.get("folder_name"))

            elif tool_name == "add_watched_folder":
                return tools.add_watched_folder(args.get("path"))

            elif tool_name == "sort_folder":
                return tools.sort_folder(args.get("folder_name"))

            elif tool_name == "process_folder":
                return tools.process_folder(
                    args.get("path"), args.get("confirmed", False)
                )

            elif tool_name == "confirm_process_folder":
                return tools.confirm_process_folder(
                    args.get("confirmation_id"), args.get("confirmed", False)
                )

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

    def generate_response(self, user_message: str) -> str:
        try:
            # Check if user is responding to a confirmation
            if self.pending_confirmation:
                return self._handle_confirmation_response(user_message)

            # Detect query type
            query_type = self._detect_query_type(user_message)
            logger.info(f"Detected query type: {query_type}")

            # Build message context
            messages = [{"role": "system", "content": self._get_system_instruction()}]

            # Add limited conversation history
            for msg in self.conversation_history[-2:]:
                messages.append({"role": "user", "content": msg["user"]})
                messages.append({"role": "assistant", "content": msg["assistant"]})

            # Add context hint to guide AI
            enhanced_message = self._inject_context_hint(user_message, query_type)

            # ONLY add RAG context for content queries (not layout queries)
            if ENABLE_RAG and query_type == "content":
                rag = self.search_files(user_message)
                if rag:
                    messages.append({"role": "system", "content": rag})

            # Add current user message
            messages.append({"role": "user", "content": enhanced_message})

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

                        # Check if this is a confirmation request
                        if result.startswith("CONFIRMATION_REQUIRED|"):
                            parts = result.split("|", 2)
                            confirmation_id = parts[1]
                            message = parts[2]

                            # Store pending confirmation
                            self.pending_confirmation = {
                                "id": confirmation_id,
                                "original_message": user_message,
                            }

                            # Extract path and file count from the message
                            # Message format: "I found X files in:\n{path}\n\n..."
                            try:
                                file_count_match = re.search(r"(\d+)\s+files?", message)
                                path_match = re.search(
                                    r"in:\s*\n\s*(.+?)\s*\n", message, re.MULTILINE
                                )

                                file_count = (
                                    file_count_match.group(1)
                                    if file_count_match
                                    else "some"
                                )
                                path = (
                                    path_match.group(1).strip()
                                    if path_match
                                    else "that folder"
                                )

                                # Create clean, natural confirmation message
                                response_text = f"I'd like to organize:\n{path}\n\nI found {file_count} files in this folder.\n\nReply with 'yes' or 'no'."
                            except:
                                # Fallback if parsing fails
                                response_text = (
                                    f"{message}\n\nReply with 'yes' or 'no'."
                                )

                            self.conversation_history.append(
                                {"user": user_message, "assistant": response_text}
                            )

                            return response_text

                        # For get_file_layout, return result directly without AI summary
                        if tool_name == "get_file_layout":
                            self.conversation_history.append(
                                {"user": user_message, "assistant": result}
                            )
                            return result

                        # For other tools, generate a natural language summary
                        confirm_msgs = [
                            {
                                "role": "system",
                                "content": "You are a helpful assistant. Provide a brief, friendly confirmation based on the SYSTEM OUTPUT. Be natural and concise. Do NOT mention RAG data or system internals.",
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

            # No tool execution needed - just conversational response
            # Remove any mentions of RAG data from conversational responses
            ai_text = re.sub(
                r"based on (?:your )?RAG data[,:]?\s*", "", ai_text, flags=re.IGNORECASE
            )
            ai_text = re.sub(
                r"according to (?:your )?RAG data[,:]?\s*",
                "",
                ai_text,
                flags=re.IGNORECASE,
            )
            ai_text = re.sub(
                r"from (?:your )?RAG data[,:]?\s*", "", ai_text, flags=re.IGNORECASE
            )

            # CRITICAL: Filter out any leaked JSON commands
            # Sometimes AI includes JSON in conversational text - we need to catch this
            if '{"tool"' in ai_text or '"args"' in ai_text:
                # Try to extract and execute the JSON
                json_match_retry = re.search(
                    r'\{[^}]*"tool"[^}]*"args"[^}]*\}', ai_text, re.DOTALL
                )
                if json_match_retry:
                    try:
                        command_data = json.loads(json_match_retry.group(0))
                        tool_name = command_data.get("tool")
                        args = command_data.get("args", {})

                        if tool_name:
                            # Execute it properly
                            result = self.execute_tool(tool_name, args)

                            # Check for confirmation
                            if result.startswith("CONFIRMATION_REQUIRED|"):
                                parts = result.split("|", 2)
                                confirmation_id = parts[1]
                                message = parts[2]

                                self.pending_confirmation = {
                                    "id": confirmation_id,
                                    "original_message": user_message,
                                }

                                # Extract path and file count
                                try:
                                    file_count_match = re.search(
                                        r"(\d+)\s+files?", message
                                    )
                                    path_match = re.search(
                                        r"in:\s*\n\s*(.+?)\s*\n", message, re.MULTILINE
                                    )

                                    file_count = (
                                        file_count_match.group(1)
                                        if file_count_match
                                        else "some"
                                    )
                                    path = (
                                        path_match.group(1).strip()
                                        if path_match
                                        else "that folder"
                                    )

                                    response_text = f"I'd like to organize:\n{path}\n\nI found {file_count} files in this folder.\n\nReply with 'yes' or 'no'."
                                except:
                                    response_text = (
                                        f"{message}\n\nReply with 'yes' or 'no'."
                                    )

                                self.conversation_history.append(
                                    {"user": user_message, "assistant": response_text}
                                )

                                return response_text

                            # For other tools, generate summary
                            if tool_name == "get_file_layout":
                                self.conversation_history.append(
                                    {"user": user_message, "assistant": result}
                                )
                                return result

                            # Generate natural summary for other tools
                            confirm_msgs = [
                                {
                                    "role": "system",
                                    "content": "Provide a brief, friendly confirmation. Be natural and concise.",
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

                            self.conversation_history.append(
                                {"user": user_message, "assistant": final_text}
                            )

                            return final_text
                    except:
                        pass

                # If we can't parse or execute it, just remove the JSON from the text
                ai_text = re.sub(
                    r'\{[^}]*"tool"[^}]*"args"[^}]*\}', "", ai_text, flags=re.DOTALL
                )
                ai_text = ai_text.strip()

                # If nothing left, give a generic response
                if not ai_text:
                    ai_text = "I'm working on that request. Let me process it properly."

            self.conversation_history.append(
                {"user": user_message, "assistant": ai_text}
            )

            return ai_text

        except Exception as e:
            logger.error(f"Chat Error: {e}")
            return "I'm having trouble processing that right now. Please check the backend logs for details."

    def _handle_confirmation_response(self, user_message: str) -> str:
        """Handle user's response to a confirmation request"""
        try:
            message_lower = user_message.lower().strip()

            # Check for affirmative responses
            affirmative = [
                "yes",
                "y",
                "yeah",
                "yep",
                "sure",
                "ok",
                "okay",
                "proceed",
                "go ahead",
                "do it",
                "confirm",
            ]
            negative = [
                "no",
                "n",
                "nope",
                "cancel",
                "stop",
                "don't",
                "nevermind",
                "never mind",
            ]

            confirmed = None
            if any(
                word == message_lower or word in message_lower for word in affirmative
            ):
                confirmed = True
            elif any(
                word == message_lower or word in message_lower for word in negative
            ):
                confirmed = False
            else:
                # Unclear response
                return "I didn't understand that. Please reply 'yes' to proceed or 'no' to cancel."

            # Execute confirmation
            confirmation_id = self.pending_confirmation["id"]
            self.pending_confirmation = None  # Clear pending state

            result = tools.confirm_process_folder(confirmation_id, confirmed)

            # Generate friendly response
            if confirmed:
                response_text = "Great! " + result
            else:
                response_text = result

            self.conversation_history.append(
                {"user": user_message, "assistant": response_text}
            )

            return response_text

        except Exception as e:
            logger.error(f"Confirmation error: {e}")
            self.pending_confirmation = None
            return "Error processing confirmation. Please try your request again."

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.pending_confirmation = None
        logger.info("Conversation history cleared")
