"""
AI Processing with Ollama (Phi-3-Mini + LLaVA-Phi3)
Generic classification that works for ANY user-defined categories
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
            "entities": List[str],
            "image_description": str
        }
        """
        result = {
            "summary": "",
            "keywords": [],
            "category_suggestions": [],
            "entities": [],
            "image_description": "",
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
                result["image_description"] = img_analysis
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
                prompt="""Describe this image accurately and objectively:
1. What is the PRIMARY content? (be specific: is it a person, artwork, screenshot, diagram, document, etc.)
2. What is the visual style? (photo, digital art, anime/cartoon, technical diagram, UI screenshot, etc.)
3. What text or important details are visible?
4. What would someone searching for this type of image be looking for?

Be precise and factual.""",
                images=[image_path],
            )

            return response["response"]

        except Exception as e:
            logger.error(f"LLaVA-Phi3 error: {e}")
            return ""

    @staticmethod
    def _calculate_semantic_match(content: str, category_name: str) -> float:
        """
        Calculate how well content matches a category name.
        Works well for both single-word and multi-word categories.
        Returns score 0.0-1.0
        """
        if not content or not category_name:
            return 0.0

        content_lower = content.lower()
        category_lower = category_name.lower()

        # Split category name into words
        category_words = set(category_lower.split())
        content_words = set(content_lower.split())

        # Remove stop words
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
        category_words = category_words - stop_words
        content_words = content_words - stop_words

        if not category_words:
            return 0.0

        # For single-word categories, give higher weight to exact matches
        is_single_word = len(category_words) == 1

        # Count matches
        matches = len(category_words.intersection(content_words))
        total_category_words = len(category_words)

        # Base score: percentage of category words found
        base_score = matches / total_category_words if total_category_words > 0 else 0.0

        # Boost for single-word categories that match
        if is_single_word and matches > 0:
            base_score = min(1.0, base_score + 0.2)

        # Bonus for exact category name phrase appearing in content
        if category_lower in content_lower:
            base_score = min(1.0, base_score + 0.3)

        # Check for plural forms (train/trains, girl/girls)
        category_singular = (
            list(category_words)[0].rstrip("s") if is_single_word else None
        )
        if category_singular and (
            category_singular in content_lower
            or category_singular + "s" in content_lower
        ):
            base_score = min(1.0, base_score + 0.2)

        return base_score

    @staticmethod
    def classify_into_categories(analysis: Dict, categories: List[Dict]) -> Dict:
        """
        Classify content into user-defined categories using AI + semantic matching.
        Works generically for ANY categories without hardcoding.
        Returns: {"category": str, "confidence": float}
        """
        if not categories or not state.ollama_client:
            return {"category": None, "confidence": 0.0}

        try:
            category_names = [c["name"] for c in categories]

            # Build comprehensive context
            context = analysis.get("summary", "")
            keywords_str = ", ".join(analysis.get("keywords", []))
            image_desc = analysis.get("image_description", "")

            # Prioritize image description for images
            if image_desc:
                full_context = f"IMAGE CONTENT: {image_desc}\n\nSUMMARY: {context}\nKEYWORDS: {keywords_str}"
            else:
                full_context = f"SUMMARY: {context}\nKEYWORDS: {keywords_str}"

            prompt = f"""You are a file organization assistant. Match files to categories based on their PRIMARY visual content.

FILE ANALYSIS:
{full_context}

AVAILABLE CATEGORIES:
{', '.join(category_names)}

MATCHING RULES:
1. Match based on what the PRIMARY subject/content is
2. Game screenshots with characters COUNT as character images (e.g., anime character from game = anime character)
3. REJECT: UI menus, settings screens, code editors, blank interfaces, diagrams/charts WITHOUT the main subject
4. ACCEPT: In-game screenshots showing the subject, artwork, photos, renders
5. For single-word categories (like "trains"), match if that's the main visual subject
6. If no clear match or PRIMARY content doesn't fit any category, respond "NONE"

Examples:
- "trains" category + image of train → MATCH
- "anime girl" category + game screenshot showing anime girl character → MATCH  
- "anime girl" category + game menu/settings screen → NO MATCH
- "lecture" category + statistics diagram → MATCH
- "lecture" category + anime character → NO MATCH

Respond in this format:
CATEGORY: <exact category name from list above, or NONE>
CONFIDENCE: <0-100>
REASONING: <why the PRIMARY content does/doesn't match>"""

            response = state.ollama_client.generate(model=PHI3_MODEL, prompt=prompt)

            output = response["response"]
            logger.debug(f"AI Classification response:\n{output}")

            # Parse AI response
            predicted_category = None
            ai_confidence = 0.0

            for line in output.split("\n"):
                if line.startswith("CATEGORY:"):
                    predicted_category = line.replace("CATEGORY:", "").strip()
                elif line.startswith("CONFIDENCE:"):
                    try:
                        conf_str = line.replace("CONFIDENCE:", "").strip()
                        conf_str = "".join(
                            c for c in conf_str if c.isdigit() or c == "."
                        )
                        ai_confidence = float(conf_str) / 100.0
                    except:
                        ai_confidence = 0.5

            # If AI said NONE or empty, return no match
            if not predicted_category or predicted_category.upper() == "NONE":
                return {"category": None, "confidence": 0.0}

            # Find best matching category from user's list
            best_match = None
            best_score = 0.0

            for cat in categories:
                # Check if AI's prediction matches this category
                cat_name_lower = cat["name"].lower()
                pred_lower = predicted_category.lower()

                if cat_name_lower in pred_lower or pred_lower in cat_name_lower:
                    # Calculate semantic match score
                    semantic_score = AIProcessor._calculate_semantic_match(
                        full_context, cat["name"]
                    )

                    # Combine AI confidence with semantic match
                    # Weight: 60% AI confidence, 40% semantic match
                    combined_score = (ai_confidence * 0.6) + (semantic_score * 0.4)

                    if combined_score > best_score:
                        best_score = combined_score
                        best_match = cat["name"]

            # Apply confidence thresholds
            if best_match:
                # Minimum confidence of 0.30 to consider it a match (lowered for single-word categories)
                if best_score < 0.30:
                    logger.debug(f"Score too low ({best_score:.2f}), rejecting match")
                    return {"category": None, "confidence": 0.0}

                # Cap maximum at 0.95 (increased slightly for very clear matches)
                best_score = min(best_score, 0.95)

                logger.info(
                    f"Classified as '{best_match}' with confidence {best_score:.2%}"
                )
                return {"category": best_match, "confidence": best_score}

            # No good match found
            return {"category": None, "confidence": 0.0}

        except Exception as e:
            logger.error(f"Classification error: {e}")
            import traceback

            traceback.print_exc()
            return {"category": None, "confidence": 0.0}
