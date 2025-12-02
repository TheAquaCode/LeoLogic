"""
Ollama Chatbot with RAG Integration & JSON Tool Use
"""

import ollama
import requests
import sys
import re
import json
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])
from utils.logger import setup_logger
from file_organizer import tools

logger = setup_logger(__name__)
from config.settings import (
    OLLAMA_HOST, PHI3_MODEL, 
    MAX_CONVERSATION_HISTORY, 
    ENABLE_RAG, FILE_ORGANIZER_PORT
)

class OllamaChatbot:
    def __init__(self):
        self.client = ollama.Client(host=OLLAMA_HOST)
        self.conversation_history = []
        self.is_ready = True
        self.loading = False
        
    def _get_system_instruction(self):
        """Strict JSON-based System Prompt"""
        status = tools.get_system_status()
        
        return f"""You are Clanky, an automated File Organizer.

Current Configuration:
- Categories: {', '.join(status['categories'])}
- Watched: {', '.join(status['watched_folders'])}

TOOLS AVAILABLE:
1. create_category(name, path) - Creates a destination category.
2. add_watched_folder(path) - Adds a source folder to monitor.
3. sort_folder(folder_name) - Manually runs sort on a watched folder.

INSTRUCTIONS:
- If the user asks to perform an action, return a JSON object ONLY.
- Format: {{ "tool": "tool_name", "args": {{ "arg1": "value" }} }}
- Example: {{ "tool": "create_category", "args": {{ "name": "Docs", "path": "Documents" }} }}
- If NO action is needed, reply with normal text.
- Do NOT output markdown code blocks (```json). Just the raw JSON string.
"""
    
    def search_files(self, query: str) -> str:
        try:
            response = requests.post(
                f"http://localhost:{FILE_ORGANIZER_PORT}/api/rag/search",
                json={"query": query, "max_results": 3},
                timeout=3
            )
            if response.status_code == 200:
                results = response.json().get("results", [])
                if not results: return None
                
                context = f"Search Results:\n"
                for res in results:
                    context += f"- {res['file']}: {res.get('summary', '')[:100]}...\n"
                return context
        except: return None
        return None

    def execute_tool(self, tool_name, args):
        """Execute parsed JSON tool"""
        try:
            logger.info(f"🔧 Tool Exec: {tool_name} {args}")

            if tool_name == "create_category":
                return tools.create_category(args.get("name"), args.get("path"))
            elif tool_name == "add_watched_folder":
                return tools.add_watched_folder(args.get("path"))
            elif tool_name == "sort_folder":
                return tools.sort_folder(args.get("folder_name"))
            else:
                return f"Error: Unknown tool {tool_name}"
        except Exception as e:
            return f"Tool Error: {str(e)}"

    def generate_response(self, user_message):
        try:
            messages = [{"role": "system", "content": self._get_system_instruction()}]
            
            # Limited history
            for msg in self.conversation_history[-2:]:
                messages.append({"role": "user", "content": msg["user"]})
                messages.append({"role": "assistant", "content": msg["assistant"]})
            
            # RAG
            if ENABLE_RAG and ("find" in user_message.lower() or "search" in user_message.lower()):
                rag = self.search_files(user_message)
                if rag: messages.append({"role": "system", "content": rag})

            messages.append({"role": "user", "content": user_message})
            
            # 1. Get AI Response
            response = self.client.chat(model=PHI3_MODEL, messages=messages)
            ai_text = response['message']['content'].strip()

            # 2. Detect JSON (Handle Markdown wrappers if AI adds them)
            # Remove markdown blocks like ```json ... ```
            clean_text = re.sub(r'```json\s*', '', ai_text)
            clean_text = re.sub(r'```', '', clean_text).strip()

            json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
            
            if json_match:
                try:
                    command_data = json.loads(json_match.group(0))
                    tool_name = command_data.get("tool")
                    args = command_data.get("args", {})
                    
                    if tool_name:
                        # Execute
                        result = self.execute_tool(tool_name, args)
                        
                        # 3. Summarize result
                        confirm_msgs = [
                            {"role": "system", "content": "You are a helpful assistant. Provide a brief, one-sentence confirmation based on the SYSTEM OUTPUT. Do not mention JSON."},
                            {"role": "user", "content": f"User Request: {user_message}\nSYSTEM OUTPUT: {result}"}
                        ]
                        
                        final_resp = self.client.chat(model=PHI3_MODEL, messages=confirm_msgs)
                        final_text = final_resp['message']['content']
                        
                        self.conversation_history.append({"user": user_message, "assistant": final_text})
                        return final_text
                except json.JSONDecodeError:
                    pass
            
            # Fallback: Just return text
            self.conversation_history.append({"user": user_message, "assistant": ai_text})
            return ai_text

        except Exception as e:
            logger.error(f"Chat Error: {e}")
            return "I'm having trouble thinking right now. Check the backend logs."

    def clear_history(self):
        self.conversation_history = []