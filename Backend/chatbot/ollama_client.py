"""
Ollama Chatbot with RAG Integration
FIXED: actually searches RAG files when asked about file contents

REPLACE FILE: Backend/chatbot/ollama_client.py
"""

import ollama
import requests
import sys
import re
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])
from utils.logger import setup_logger

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
        self.system_instruction = """You are Clanky, a helpful AI assistant for a file organization system.

Your goal is to help users find files and understand their content based on the provided search results.

GUIDELINES:
1. **Natural Tone:** Speak naturally and directly. Do NOT mention "RAG", "search_files", "tools", or "internal functions".
2. **Formatting:** Use **bold** for filenames and key concepts to make them easy to read.
3. **Conciseness:** Keep responses brief and to the point. Avoid unnecessary fluff.
4. ** honesty:** If the search results say the file wasn't found, simply state that you don't see that file in the organized folders. Don't make excuses about tools.

IMPORTANT: When the system provides "File search results", rely EXACTLY on that information. Do not hallucinate content if it's not there."""
    
    def search_files(self, query: str) -> str:
        """
        Search through RAG files for relevant information
        """
        try:
            logger.info(f"🔍 Searching RAG files for: {query}")
            
            response = requests.post(
                f"http://localhost:{FILE_ORGANIZER_PORT}/api/rag/search",
                json={"query": query, "max_results": 5},
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json().get("results", [])
                
                if not results:
                    return f"System Notification: No files found matching '{query}' in the index."
                
                # Format results for the chatbot
                context = f"Here is the content found for the user's query '{query}':\n\n"
                for i, result in enumerate(results, 1):
                    context += f"📄 **{result['file']}** (Location: {result['path']})\n"
                    if result.get('summary'):
                        context += f"   Summary: {result['summary']}\n"
                    if result.get('keywords'):
                        context += f"   Keywords: {', '.join(result['keywords'][:5])}\n"
                    if result.get('content_preview'):
                        preview = result['content_preview'][:300]
                        context += f"   Content Snippet: {preview}...\n"
                    context += "\n"
                
                return context
            else:
                return "System Notification: Search service is currently unavailable."
            
        except Exception as e:
            logger.error(f"RAG search error: {e}")
            return "System Notification: Unable to perform search due to a connection error."
    
    def generate_response(self, user_message, store_history=True):
        """Generate response with RAG context when needed"""
        try:
            messages = [{"role": "system", "content": self.system_instruction}]
            
            # Add conversation history
            for msg in self.conversation_history[-MAX_CONVERSATION_HISTORY:]:
                messages.append({"role": "user", "content": msg["user"]})
                messages.append({"role": "assistant", "content": msg["assistant"]})
            
            # Check if user is asking about files
            rag_context = ""
            if ENABLE_RAG and self._should_use_rag(user_message):
                logger.info(f"📚 User query needs RAG search: {user_message}")
                rag_context = self.search_files(user_message)
                
                if rag_context:
                    # Add RAG results as context
                    messages.append({
                        "role": "system",
                        "content": f"{rag_context}\n\nUse the information above to answer the user's question."
                    })
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            logger.info("🤖 Generating response with Phi3...")
            
            # Generate response
            response = self.client.chat(
                model=PHI3_MODEL,
                messages=messages
            )
            
            response_text = response['message']['content']
            
            # Save to history
            if store_history:
                self.conversation_history.append({
                    "user": user_message,
                    "assistant": response_text
                })
            
            return response_text
        
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return f"I encountered an error connecting to my brain. Please ensure the backend is running."
    
    def _should_use_rag(self, message: str) -> bool:
        """Determine if query needs file search"""
        rag_keywords = [
            'file', 'document', 'find', 'search', 'what did', 
            'show me', 'where is', 'tell me about', 'what is in',
            'read', 'open', 'contents', 'content of',
            'pdf', 'word', 'excel', 'txt', '.txt', '.pdf', '.docx',
            'summary', 'summarize'
        ]
        message_lower = message.lower()
        
        # Check for keywords
        has_keyword = any(keyword in message_lower for keyword in rag_keywords)
        
        # Check for file extensions
        has_extension = any(ext in message_lower for ext in ['.txt', '.pdf', '.docx', '.xlsx', '.pptx'])
        
        return has_keyword or has_extension
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("🗑️  Conversation history cleared")