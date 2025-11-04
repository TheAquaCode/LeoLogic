"""
Ollama Chatbot with RAG Integration
"""

import ollama
import requests
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
        self.system_instruction = """You are a helpful AI assistant for Leologic, an AI-powered file organization system.

You help users:
1. Organize and find their files
2. Answer questions about file contents
3. Provide summaries of documents
4. Search through organized files

When users ask about their files, you can search through them using the RAG system."""
    
    def generate_response(self, user_message, store_history=True):
        """Generate response with optional RAG context"""
        try:
            messages = [{"role": "system", "content": self.system_instruction}]
            
            # Add conversation history
            for msg in self.conversation_history[-MAX_CONVERSATION_HISTORY:]:
                messages.append({"role": "user", "content": msg["user"]})
                messages.append({"role": "assistant", "content": msg["assistant"]})
            
            # Check if we should use RAG
            rag_context = ""
            if ENABLE_RAG and self._should_use_rag(user_message):
                rag_context = self._get_rag_context(user_message)
                if rag_context:
                    messages.append({
                        "role": "system",
                        "content": f"Relevant file information:\n{rag_context}"
                    })
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
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
            print(f"❌ Error generating response: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {str(e)}"
    
    def _should_use_rag(self, message: str) -> bool:
        """Determine if query needs file search"""
        rag_keywords = [
            'file', 'document', 'find', 'search', 'what did', 
            'show me', 'where is', 'tell me about', 'summary',
            'contents', 'pdf', 'word', 'excel', 'image', 'video'
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in rag_keywords)
    
    def _get_rag_context(self, query: str) -> str:
        """Get relevant context from RAG system"""
        try:
            # Call file organizer's RAG search endpoint
            response = requests.post(
                f"http://localhost:{FILE_ORGANIZER_PORT}/api/rag/search",
                json={"query": query, "max_results": 3}
            )
            
            if response.status_code == 200:
                results = response.json().get("results", [])
                
                if not results:
                    return ""
                
                # Format results as context
                context = "Here are relevant files:\n\n"
                for i, result in enumerate(results, 1):
                    context += f"{i}. **{result['file']}**\n"
                    context += f"   Summary: {result['summary']}\n"
                    context += f"   Keywords: {', '.join(result['keywords'])}\n"
                    context += f"   Preview: {result['content_preview'][:200]}...\n\n"
                
                return context
            
        except Exception as e:
            print(f"⚠️ RAG search error: {e}")
        
        return ""
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
