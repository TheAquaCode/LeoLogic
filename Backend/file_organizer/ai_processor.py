"""
AI Processing with Ollama (Phi-3-Mini + LLaVA-Phi3)
"""

import ollama
from pathlib import Path
from typing import Dict, List
from config.settings import PHI3_MODEL, LLAVA_MODEL
from .state import state
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AIProcessor:
    """Process extracted content with AI models"""

    @staticmethod
    def analyze_content(extracted_data: Dict) -> Dict:
        """
        Analyze extracted content using appropriate AI models.
        Returns: {
            "summary": str,
            "keywords": List[str],
            "category_suggestions": List[str],
            "entities": List[str]
        }
        """
        result = {
            "summary": "",
            "keywords": [],
            "category_suggestions": [],
            "entities": [],
        }

        # Process text with Phi-3-Mini
        if extracted_data.get("text"):
            text_analysis = AIProcessor._analyze_text(extracted_data["text"])
            result.update(text_analysis)

        # Process audio transcript
        if extracted_data.get("audio_transcript"):
            audio_analysis = AIProcessor._analyze_text(
                f"Audio transcript: {extracted_data['audio_transcript']}"
            )
            result["summary"] += "\n\nAudio: " + audio_analysis.get("summary", "")

        # Process images with LLaVA-Phi3
        if extracted_data.get("images"):
            for img_path in extracted_data["images"]:
                img_analysis = AIProcessor._analyze_image(img_path)
                result["summary"] += "\n\nImage: " + img_analysis

        return result

    @staticmethod
    def _analyze_text(text: str) -> Dict:
        """Analyze text with Phi-3-Mini"""
        if not state.ollama_client or not text.strip():
            return {"summary": "", "keywords": [], "category_suggestions": []}

        try:
            # Truncate very long text
            if len(text) > 4000:
                text = text[:4000] + "..."

            prompt = f"""Analyze this document and provide:
1. A brief summary (2-3 sentences)
2. 5 key keywords
3. 3 category suggestions for organizing this file

Document:
{text}

Respond in this format:
SUMMARY: <summary>
KEYWORDS: <keyword1>, <keyword2>, ...
CATEGORIES: <category1>, <category2>, <category3>
"""

            response = state.ollama_client.generate(model=PHI3_MODEL, prompt=prompt)

            output = response["response"]

            # Parse response
            result = {"summary": "", "keywords": [], "category_suggestions": []}

            for line in output.split("\n"):
                if line.startswith("SUMMARY:"):
                    result["summary"] = line.replace("SUMMARY:", "").strip()
                elif line.startswith("KEYWORDS:"):
                    keywords = line.replace("KEYWORDS:", "").strip()
                    result["keywords"] = [k.strip() for k in keywords.split(",")]
                elif line.startswith("CATEGORIES:"):
                    categories = line.replace("CATEGORIES:", "").strip()
                    result["category_suggestions"] = [
                        c.strip() for c in categories.split(",")
                    ]

            return result

        except Exception as e:
            logger.error(f"Phi-3-Mini error: {e}")
            return {"summary": "", "keywords": [], "category_suggestions": []}

    @staticmethod
    def _analyze_image(image_path: str) -> str:
        """Analyze image with LLaVA-Phi3"""
        if not state.ollama_client:
            return ""

        try:
            response = state.ollama_client.generate(
                model=LLAVA_MODEL,
                prompt="Describe this image in detail. What is the main subject? What text or important elements are visible?",
                images=[image_path],
            )

            return response["response"]

        except Exception as e:
            logger.error(f"LLaVA-Phi3 error: {e}")
            return ""

    @staticmethod
    def _calculate_similarity_score(text1: str, text2: str) -> float:
        """
        Calculate simple word overlap similarity between two texts.
        Returns a score between 0.0 and 1.0.
        """
        if not text1 or not text2:
            return 0.0

        # Normalize and tokenize
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        # Remove very common words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        }
        words1 = words1 - stop_words
        words2 = words2 - stop_words

        if not words1 or not words2:
            return 0.0

        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    @staticmethod
    def classify_into_categories(analysis: Dict, categories: List[Dict]) -> Dict:
        """
        Use AI to classify into user-defined categories with REAL confidence scoring.
        Returns: {"category": str, "confidence": float}
        """
        if not categories or not state.ollama_client:
            return {"category": None, "confidence": 0.0}

        try:
            category_names = [c["name"] for c in categories]

            # Build context from analysis
            context = f"{analysis.get('summary', '')} {' '.join(analysis.get('keywords', []))}"

            prompt = f"""Given this file analysis, which category fits best? Rate your confidence from 0-100.

Summary: {analysis.get('summary', '')}
Keywords: {', '.join(analysis.get('keywords', []))}

Available categories: {', '.join(category_names)}

Respond ONLY in this exact format:
CATEGORY: <category_name>
CONFIDENCE: <number from 0-100>
REASONING: <brief explanation>"""

            response = state.ollama_client.generate(model=PHI3_MODEL, prompt=prompt)

            output = response["response"]

            # Parse response
            predicted_category = None
            ai_confidence = 0.0

            for line in output.split("\n"):
                if line.startswith("CATEGORY:"):
                    predicted_category = line.replace("CATEGORY:", "").strip()
                elif line.startswith("CONFIDENCE:"):
                    try:
                        conf_str = line.replace("CONFIDENCE:", "").strip()
                        # Extract just the number
                        conf_str = "".join(
                            c for c in conf_str if c.isdigit() or c == "."
                        )
                        ai_confidence = float(conf_str) / 100.0  # Convert to 0-1 range
                    except:
                        ai_confidence = 0.5  # Default if parsing fails

            # Find best matching category
            best_match = None
            best_score = 0.0

            for cat in categories:
                # Check direct name match
                if (
                    predicted_category
                    and cat["name"].lower() in predicted_category.lower()
                ):
                    # Calculate similarity score between context and category name
                    similarity = AIProcessor._calculate_similarity_score(
                        context, cat["name"]
                    )

                    # Combine AI confidence with similarity score
                    combined_score = (ai_confidence * 0.7) + (similarity * 0.3)

                    if combined_score > best_score:
                        best_score = combined_score
                        best_match = cat["name"]

            # If no direct match, try matching with AI's category suggestions
            if not best_match and analysis.get("category_suggestions"):
                for suggestion in analysis["category_suggestions"]:
                    for cat in categories:
                        similarity = AIProcessor._calculate_similarity_score(
                            suggestion, cat["name"]
                        )
                        if similarity > 0.3:  # Threshold for indirect match
                            combined_score = (
                                similarity * 0.6
                            )  # Lower confidence for indirect matches
                            if combined_score > best_score:
                                best_score = combined_score
                                best_match = cat["name"]

            # Cap minimum confidence at 0.3 if we found a match
            if best_match and best_score > 0:
                best_score = max(best_score, 0.3)

            # Cap maximum confidence at 0.95
            best_score = min(best_score, 0.95)

            logger.debug(f"Classification result: {best_match} ({best_score:.2%})")

            return {"category": best_match, "confidence": best_score}

        except Exception as e:
            logger.error(f"Classification error: {e}")
            return {"category": None, "confidence": 0.0}
