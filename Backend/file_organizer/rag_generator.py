"""
RAG (Retrieval Augmented Generation) System
Stores processed files in searchable format for chatbot
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from config.settings import RAG_DIR, CHUNK_SIZE, CHUNK_OVERLAP


class RAGGenerator:
    """Generate and store RAG data for files"""
    
    @staticmethod
    def create_rag_document(
        file_path: str,
        extracted_data: Dict,
        ai_analysis: Dict,
        category: str
    ) -> str:
        """
        Create a RAG document with all file information.
        Returns: Path to RAG JSON file
        """
        file_name = Path(file_path).stem
        rag_filename = f"{file_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.rag.json"
        rag_path = RAG_DIR / rag_filename
        
        # Chunk the text content
        full_text = extracted_data.get("text", "")
        if extracted_data.get("audio_transcript"):
            full_text += "\n\nAudio Transcript:\n" + extracted_data["audio_transcript"]
        
        chunks = RAGGenerator._chunk_text(full_text)
        
        # Create RAG document
        rag_doc = {
            "file_info": {
                "original_path": file_path,
                "filename": Path(file_path).name,
                "category": category,
                "file_type": extracted_data.get("file_type", "unknown"),
                "created_at": datetime.now().isoformat()
            },
            "content": {
                "full_text": full_text[:10000],  # Store first 10k chars
                "chunks": chunks,
                "audio_transcript": extracted_data.get("audio_transcript", ""),
                "images": extracted_data.get("images", [])
            },
            "analysis": {
                "summary": ai_analysis.get("summary", ""),
                "keywords": ai_analysis.get("keywords", []),
                "entities": ai_analysis.get("entities", []),
                "category_suggestions": ai_analysis.get("category_suggestions", [])
            },
            "metadata": extracted_data.get("metadata", {})
        }
        
        # Save RAG document
        with open(rag_path, 'w', encoding='utf-8') as f:
            json.dump(rag_doc, f, indent=2, ensure_ascii=False)
        
        print(f"💾 RAG document created: {rag_path}")
        return str(rag_path)
    
    @staticmethod
    def _chunk_text(text: str) -> List[str]:
        """Split text into overlapping chunks"""
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + CHUNK_SIZE
            chunk = text[start:end]
            chunks.append(chunk)
            start += CHUNK_SIZE - CHUNK_OVERLAP
        
        return chunks
    
    @staticmethod
    def search_rag(query: str, max_results: int = 5) -> List[Dict]:
        """
        Search through all RAG documents for relevant information.
        Returns list of relevant documents with scores.
        """
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Search through all RAG files
        for rag_file in RAG_DIR.glob("*.rag.json"):
            try:
                with open(rag_file, 'r', encoding='utf-8') as f:
                    rag_doc = json.load(f)
                
                # Calculate relevance score
                score = 0
                
                # Check summary
                summary = rag_doc.get("analysis", {}).get("summary", "").lower()
                score += sum(word in summary for word in query_words) * 3
                
                # Check keywords
                keywords = [k.lower() for k in rag_doc.get("analysis", {}).get("keywords", [])]
                score += sum(word in keywords for word in query_words) * 5
                
                # Check chunks
                for chunk in rag_doc.get("content", {}).get("chunks", []):
                    chunk_lower = chunk.lower()
                    score += sum(word in chunk_lower for word in query_words)
                
                # Check audio transcript
                transcript = rag_doc.get("content", {}).get("audio_transcript", "").lower()
                score += sum(word in transcript for word in query_words) * 2
                
                if score > 0:
                    results.append({
                        "file": rag_doc["file_info"]["filename"],
                        "path": rag_doc["file_info"]["original_path"],
                        "summary": rag_doc["analysis"]["summary"],
                        "keywords": rag_doc["analysis"]["keywords"],
                        "score": score,
                        "content_preview": rag_doc["content"]["full_text"][:500]
                    })
            
            except Exception as e:
                print(f"⚠️ Error reading RAG file {rag_file}: {e}")
                continue
        
        # Sort by score and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
