"""
RAG (Retrieval Augmented Generation) System
Stores processed files in searchable format for chatbot.
Smart updates: Updates existing records instead of creating duplicates.
"""

import json
import hashlib
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from config.settings import RAG_DATA_DIR as RAG_DIR, CHUNK_SIZE, CHUNK_OVERLAP


class RAGGenerator:
    """Generate and store RAG data for files"""

    @staticmethod
    def _generate_hash(file_path: Path) -> str:
        """
        Generate a hash based on filename, size, and modification time.
        Strictly content-based. Path is irrelevant to the hash.
        """
        try:
            stats = file_path.stat()
            # Key = Filename + Size + ModifiedTime
            key = f"{file_path.name}_{stats.st_size}_{stats.st_mtime}"
            return hashlib.md5(key.encode()).hexdigest()
        except Exception:
            # Fallback
            return hashlib.md5(file_path.name.encode()).hexdigest()

    @staticmethod
    def get_rag_filename(file_path: Path) -> Path:
        """Calculate the expected RAG filename for a specific file state."""
        cache_hash = RAGGenerator._generate_hash(file_path)
        return RAG_DIR / f"{file_path.stem}_{cache_hash}.rag.json"

    @staticmethod
    def create_rag_document(
        file_path: str, extracted_data: Dict, ai_analysis: Dict, category: str
    ) -> str:
        """
        Create OR Update a RAG document.
        If an identical RAG file exists, just update the path inside it.
        """
        try:
            path_obj = Path(file_path)
            if not path_obj.exists():
                return None

            # Ensure RAG directory exists
            RAG_DIR.mkdir(parents=True, exist_ok=True)

            # 1. Calculate the hash for the CURRENT file state
            current_hash = RAGGenerator._generate_hash(path_obj)
            target_rag_filename = f"{path_obj.stem}_{current_hash}.rag.json"
            target_rag_path = RAG_DIR / target_rag_filename

            # 2. Check for ANY existing RAG files for this filename stem
            # This handles the cleanup of old versions or duplicates
            existing_rags = list(RAG_DIR.glob(f"{path_obj.stem}_*.rag.json"))
            
            rag_already_exists = False

            for existing_rag in existing_rags:
                # If the filename matches exactly, we have the exact same file content/version
                if existing_rag.name == target_rag_filename:
                    rag_already_exists = True
                    # Just update the path inside the JSON (in case file moved)
                    try:
                        with open(existing_rag, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Only write if path actually changed
                        if data.get('file_info', {}).get('original_path') != str(file_path):
                            data['file_info']['original_path'] = str(file_path)
                            data['file_info']['category'] = category
                            with open(existing_rag, 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
                            print(f"  ♻️ Updated path in existing RAG: {existing_rag.name}")
                        else:
                            print(f"  ✅ RAG up to date: {existing_rag.name}")
                            
                    except Exception as e:
                        print(f"  ⚠️ Error updating existing RAG: {e}")
                        # If corrupt, treat as not existing
                        rag_already_exists = False
                else:
                    # This is an old version (hash mismatch) or a duplicate. Delete it.
                    try:
                        os.remove(existing_rag)
                        print(f"  🧹 Pruned stale RAG: {existing_rag.name}")
                    except Exception:
                        pass

            # 3. If we found the exact match, we are done. Return.
            if rag_already_exists:
                return str(target_rag_path)

            # 4. If we are here, it's a new file or new version. Create fresh RAG.
            
            # Chunk the text content
            full_text = extracted_data.get("text", "")
            if extracted_data.get("audio_transcript"):
                full_text += (
                    "\n\nAudio Transcript:\n" + extracted_data["audio_transcript"]
                )

            chunks = RAGGenerator._chunk_text(full_text)

            rag_doc = {
                "file_info": {
                    "original_path": file_path,
                    "filename": path_obj.name,
                    "category": category,
                    "file_type": extracted_data.get("file_type", "unknown"),
                    "created_at": datetime.now().isoformat(),
                },
                "content": {
                    "full_text": full_text[:10000],
                    "chunks": chunks,
                    "audio_transcript": extracted_data.get("audio_transcript", ""),
                    "images": extracted_data.get("images", []),
                },
                "analysis": {
                    "summary": ai_analysis.get("summary", ""),
                    "keywords": ai_analysis.get("keywords", []),
                    "entities": ai_analysis.get("entities", []),
                    "category_suggestions": ai_analysis.get("category_suggestions", []),
                },
                "metadata": extracted_data.get("metadata", {}),
            }

            with open(target_rag_path, "w", encoding="utf-8") as f:
                json.dump(rag_doc, f, indent=2, ensure_ascii=False)

            print(f"💾 Created NEW RAG document: {target_rag_path.name}")
            return str(target_rag_path)

        except Exception as e:
            print(f"  ⚠️  Error creating RAG document: {e}")
            import traceback
            traceback.print_exc()
            return None

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
        """
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())

        for rag_file in RAG_DIR.glob("*.rag.json"):
            try:
                with open(rag_file, "r", encoding="utf-8") as f:
                    rag_doc = json.load(f)

                score = 0
                
                # Simple keyword scoring
                filename = rag_doc.get("file_info", {}).get("filename", "").lower()
                if query_lower in filename: score += 10

                summary = rag_doc.get("analysis", {}).get("summary", "").lower()
                score += sum(word in summary for word in query_words) * 3

                keywords = [k.lower() for k in rag_doc.get("analysis", {}).get("keywords", [])]
                score += sum(word in keywords for word in query_words) * 5

                # Search content chunks
                for chunk in rag_doc.get("content", {}).get("chunks", []):
                    if any(word in chunk.lower() for word in query_words):
                        score += 1

                if score > 0:
                    results.append({
                        "file": rag_doc["file_info"]["filename"],
                        "path": rag_doc["file_info"]["original_path"],
                        "summary": rag_doc["analysis"]["summary"],
                        "keywords": rag_doc["analysis"]["keywords"],
                        "score": score,
                        "content_preview": rag_doc["content"]["full_text"][:500],
                    })

            except Exception:
                continue

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]