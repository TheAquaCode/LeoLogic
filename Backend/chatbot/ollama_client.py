"""
Ollama Chatbot with RAG Integration
FIXED: Actually searches RAG files when asked about file contents

REPLACE FILE: Backend/chatbot/ollama_client.py
"""

import ollama
import requests
import sys
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
        self.system_instruction = """You are Clanky, a helpful AI assistant for an AI-powered file organization system.

You help users:
1. Find and retrieve information from their organized files
2. Answer questions about file contents using the RAG system
3. Provide summaries of documents
4. Search through organized files

IMPORTANT: When users ask about a specific file (like "what's in work.txt" or "tell me about sales report"), 
you MUST search the RAG system using the search_files tool to find that file's contents.

Always search first, then answer based on the actual file contents you find."""
    
    def search_files(self, query: str) -> str:
        """
        Search through RAG files for relevant information
        
        Args:
            query: Search query (can be filename or content-based query)
        
        Returns:
            Formatted string with search results
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
                    return f"No files found matching '{query}'. The file may not have been processed yet, or it might not exist in the organized folders."
                
                # Format results for the chatbot
                context = f"Found {len(results)} relevant file(s):\n\n"
                for i, result in enumerate(results, 1):
                    context += f"📄 **{result['file']}**\n"
                    context += f"   Location: {result['path']}\n"
                    if result.get('summary'):
                        context += f"   Summary: {result['summary']}\n"
                    if result.get('keywords'):
                        context += f"   Keywords: {', '.join(result['keywords'][:5])}\n"
                    if result.get('content_preview'):
                        preview = result['content_preview'][:300]
                        context += f"   Content: {preview}...\n"
                    context += "\n"
                
                logger.info(f"✅ Found {len(results)} files")
                return context
            else:
                logger.error(f"RAG search failed with status {response.status_code}")
                return "Error searching files. The file organization service may not be running."
            
        except requests.exceptions.Timeout:
            logger.error("RAG search timeout")
            return "Search timeout. The file organization service is taking too long to respond."
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to file organizer service")
            return "Cannot connect to file organization service. Make sure it's running on port 5001."
        except Exception as e:
            logger.error(f"RAG search error: {e}")
            return f"Error searching files: {str(e)}"
    
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
                
                if rag_context and "No files found" not in rag_context and "Error" not in rag_context:
                    # Add RAG results as context
                    messages.append({
                        "role": "system",
                        "content": f"File search results:\n{rag_context}\n\nUse this information to answer the user's question."
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
            
            # If RAG found nothing and user was asking about a file, be helpful
            if rag_context and "No files found" in rag_context:
                response_text = f"I couldn't find a file matching '{user_message}'. This could mean:\n\n" \
                              f"1. The file hasn't been processed yet by the AI organizer\n" \
                              f"2. The file might be in a watched folder that needs scanning\n" \
                              f"3. The filename might be different\n\n" \
                              f"Try:\n" \
                              f"- Processing the folder containing the file in the File Explorer tab\n" \
                              f"- Checking if the file is in a watched folder\n" \
                              f"- Searching for keywords from the file instead of the exact filename"
            
            # Save to history
            if store_history:
                self.conversation_history.append({
                    "user": user_message,
                    "assistant": response_text
                })
            
            logger.info("✅ Response generated")
            return response_text
        
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            return f"I encountered an error: {str(e)}\n\nMake sure the file organization service is running and you've processed some files."
    
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