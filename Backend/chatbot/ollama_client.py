"""
Ollama Chatbot with RAG Integration
"""

import ollama
import requests
import json
import sys
from pathlib import Path

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from utils.logger import setup_logger

logger = setup_logger(__name__)
from config.settings import (
    OLLAMA_HOST,
    PHI3_MODEL,
    MAX_CONVERSATION_HISTORY,
    ENABLE_RAG,
    FILE_ORGANIZER_PORT,
    RAG_DATA_DIR,
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
2. Answer questions about file contents (homework, documents, images, etc.)
3. Provide summaries of documents
4. Search through organized files

When users ask about their files, homework, documents, or anything stored on their computer, you search through the RAG system to find relevant information and provide helpful answers based on the file contents."""

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
                    messages.append(
                        {
                            "role": "system",
                            "content": f"Relevant information from user's files:\n\n{rag_context}\n\nUse this information to answer the user's question.",
                        }
                    )
                    logger.info(f"RAG context added: {len(rag_context)} characters")
                else:
                    logger.info("No relevant RAG context found")

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Generate response
            response = self.client.chat(model=PHI3_MODEL, messages=messages)

            response_text = response["message"]["content"]

            # Save to history
            if store_history:
                self.conversation_history.append(
                    {"user": user_message, "assistant": response_text}
                )

            return response_text

        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            import traceback

            traceback.print_exc()
            return f"Error: {str(e)}"

    def _should_use_rag(self, message: str) -> bool:
        """Determine if query needs file search"""
        # Expanded keywords for homework and document queries
        rag_keywords = [
            # Files and documents
            "file",
            "document",
            "find",
            "search",
            "show me",
            "where is",
            "pdf",
            "word",
            "excel",
            "image",
            "video",
            "text",
            "doc",
            # Homework and academic
            "homework",
            "assignment",
            "essay",
            "paper",
            "project",
            "study",
            "notes",
            "lecture",
            "class",
            "course",
            "test",
            "exam",
            "quiz",
            # Content queries
            "what did",
            "tell me about",
            "summary",
            "summarize",
            "contents",
            "information about",
            "details about",
            "explain",
            "describe",
            # Database and code
            "database",
            "schema",
            "table",
            "code",
            "program",
            "script",
            # General search terms
            "have",
            "got",
            "stored",
            "saved",
            "uploaded",
            "my",
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in rag_keywords)

    def _get_rag_context(self, query: str) -> str:
        """Get relevant context from RAG system - tries multiple methods"""

        # Method 1: Try the file organizer API endpoint
        try:
            response = requests.post(
                f"http://localhost:{FILE_ORGANIZER_PORT}/api/rag/search",
                json={"query": query, "max_results": 5},
                timeout=5,
            )

            if response.status_code == 200:
                results = response.json().get("results", [])

                if results:
                    logger.info(f"Found {len(results)} results via API")
                    return self._format_rag_results(results)
        except Exception as e:
            logger.warning(f"API RAG search failed: {e}, trying direct search...")

        # Method 2: Direct search through RAG files (fallback)
        try:
            results = self._direct_rag_search(query, max_results=5)
            if results:
                logger.info(f"Found {len(results)} results via direct search")
                return self._format_rag_results(results)
        except Exception as e:
            logger.error(f"Direct RAG search failed: {e}")

        return ""

    def _direct_rag_search(self, query: str, max_results: int = 5) -> list:
        """
        Directly search through RAG JSON files without needing the API.
        This is a fallback method if the file organizer API is down.
        """
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())

        # Search through all RAG files in the rag_data directory
        rag_dir = Path(RAG_DATA_DIR)

        if not rag_dir.exists():
            logger.warning(f"RAG directory does not exist: {rag_dir}")
            return []

        rag_files = list(rag_dir.glob("*.rag.json"))
        logger.info(f"Searching through {len(rag_files)} RAG files")

        for rag_file in rag_files:
            try:
                with open(rag_file, "r", encoding="utf-8") as f:
                    rag_doc = json.load(f)

                # Calculate relevance score
                score = 0

                # Check filename
                filename = rag_doc.get("file_info", {}).get("filename", "").lower()
                score += sum(word in filename for word in query_words) * 10

                # Check summary
                summary = rag_doc.get("analysis", {}).get("summary", "").lower()
                score += sum(word in summary for word in query_words) * 3

                # Check keywords
                keywords = [
                    k.lower() for k in rag_doc.get("analysis", {}).get("keywords", [])
                ]
                score += sum(word in keywords for word in query_words) * 5

                # Check full text content
                full_text = rag_doc.get("content", {}).get("full_text", "").lower()
                score += sum(word in full_text for word in query_words) * 2

                # Check chunks
                for chunk in rag_doc.get("content", {}).get("chunks", []):
                    chunk_lower = chunk.lower()
                    # Phrase matching gets bonus points
                    if query_lower in chunk_lower:
                        score += 20
                    score += sum(word in chunk_lower for word in query_words)

                # Check audio transcript
                transcript = (
                    rag_doc.get("content", {}).get("audio_transcript", "").lower()
                )
                score += sum(word in transcript for word in query_words) * 2

                if score > 0:
                    results.append(
                        {
                            "file": rag_doc["file_info"]["filename"],
                            "path": rag_doc["file_info"]["original_path"],
                            "summary": rag_doc["analysis"]["summary"],
                            "keywords": rag_doc["analysis"]["keywords"],
                            "score": score,
                            "content_preview": rag_doc["content"]["full_text"][:1000],
                            "file_type": rag_doc["file_info"].get(
                                "file_type", "unknown"
                            ),
                            "chunks": rag_doc.get("content", {}).get("chunks", []),
                        }
                    )

            except Exception as e:
                logger.warning(f"Error reading RAG file {rag_file}: {e}")
                continue

        # Sort by score and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]

    def _format_rag_results(self, results: list) -> str:
        """Format RAG results into a context string for the LLM"""
        if not results:
            return ""

        context_parts = []

        for i, result in enumerate(results, 1):
            file_name = result.get("file", result.get("filename", "Unknown"))
            file_type = result.get("file_type", "unknown")
            summary = result.get("summary", "No summary available")
            keywords = result.get("keywords", [])
            content_preview = result.get("content_preview", "")
            chunks = result.get("chunks", [])

            # Build context for this file
            file_context = f"--- File {i}: {file_name} ({file_type}) ---\n"

            if summary and summary.strip():
                file_context += f"Summary: {summary}\n"

            if keywords:
                file_context += f"Keywords: {', '.join(keywords)}\n"

            # Add relevant content chunks or preview
            if chunks:
                file_context += f"\nRelevant Content:\n"
                # Add first 2 chunks if available
                for chunk in chunks[:2]:
                    if chunk.strip():
                        file_context += f"{chunk[:500]}...\n\n"
            elif content_preview and content_preview.strip():
                file_context += f"\nContent Preview:\n{content_preview[:500]}...\n"

            context_parts.append(file_context)

        return "\n\n".join(context_parts)

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
