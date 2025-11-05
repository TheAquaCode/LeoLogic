"""
AI Processing with Ollama (Phi-3-Mini + LLaVA-Phi3)
Generic classification with detailed category breakdown
"""

import re
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
    def _calculate_semantic_match(content: str, category_name: str) -> tuple:
        """
        Calculate how well content matches a category name.
        Parses numbered points from image analysis (1., 2., 3., etc.)
        Returns: (score: float, matched_points: list)
        """
        if not content or not category_name:
            return 0.0, []

        content_lower = content.lower()
        category_lower = category_name.lower()

        # Define common synonyms for categories
        synonyms = {
            "female": [
                "girl",
                "woman",
                "lady",
                "ladies",
                "feminine",
                "she",
                "her",
                "women",
            ],
            "male": ["boy", "man", "guy", "masculine", "he", "him", "men"],
            "anime": ["manga", "japanese animation", "animated", "cartoon"],
            "car": ["automobile", "vehicle", "auto"],
            "train": ["railway", "locomotive", "rail"],
            "lecture": ["presentation", "lesson", "educational", "teaching"],
        }

        # Extract all numbered points to check separately
        numbered_points = []
        for line in content.split("\n"):
            if any(line.strip().startswith(f"{i}.") for i in range(1, 10)):
                numbered_points.append(line.lower())

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
            "from",
            "as",
            "is",
            "are",
        }
        category_words = category_words - stop_words
        content_words = content_words - stop_words

        if not category_words:
            return 0.0, []

        # Check for synonym matches in ALL content
        synonym_boost = 0.0
        matched_points = []

        for cat_word in category_words:
            if cat_word in synonyms:
                # Check if any synonym appears in ANY numbered point
                for syn in synonyms[cat_word]:
                    # Check main content
                    if syn in content_lower:
                        synonym_boost = max(synonym_boost, 0.4)

                    # Check each numbered point individually
                    for i, point in enumerate(numbered_points, 1):
                        if syn in point:
                            synonym_boost = max(synonym_boost, 0.5)
                            if f"Point {i}" not in matched_points:
                                matched_points.append(f"Point {i}: '{syn}'")

        # For single-word categories
        is_single_word = len(category_words) == 1

        # Count direct matches
        matches = len(category_words.intersection(content_words))
        total_category_words = len(category_words)

        # Base score: percentage of category words found
        base_score = matches / total_category_words if total_category_words > 0 else 0.0

        # Add synonym boost
        base_score = min(1.0, base_score + synonym_boost)

        # Boost for single-word categories that match
        if is_single_word and matches > 0:
            base_score = min(1.0, base_score + 0.2)
            if not matched_points:
                matched_points.append("Direct word match")

        # Bonus for exact category name phrase appearing in content
        if category_lower in content_lower:
            base_score = min(1.0, base_score + 0.3)
            if not matched_points:
                matched_points.append("Exact phrase match")

        # Check for plural forms
        if is_single_word and category_words:
            category_singular = list(category_words)[0].rstrip("s")
            if category_singular:
                # Check main content
                if (
                    category_singular in content_lower
                    or (category_singular + "s") in content_lower
                ):
                    base_score = min(1.0, base_score + 0.2)
                    if not matched_points:
                        matched_points.append(f"Plural form: '{category_singular}'")

                # Also check numbered points
                for i, point in enumerate(numbered_points, 1):
                    if category_singular in point or (category_singular + "s") in point:
                        base_score = min(1.0, base_score + 0.1)
                        if f"Point {i}" not in [
                            m.split(":")[0] for m in matched_points
                        ]:
                            matched_points.append(f"Point {i}: plural")

        return base_score, matched_points

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

            # Build comprehensive context - EXTRACT ALL KEY POINTS
            context = analysis.get("summary", "")
            keywords_str = ", ".join(analysis.get("keywords", []))
            image_desc = analysis.get("summery", "")

            # Parse numbered points from BOTH summary and image_description
            key_visual_elements = []
            text_to_parse = context

            if text_to_parse:
                lines = text_to_parse.split("\n")
                for line in lines:
                    # Extract numbered points (1., 2., 3., etc.)
                    if any(line.strip().startswith(f"{i}.") for i in range(1, 10)):
                        # Remove the number prefix
                        clean_line = line.strip()
                        for i in range(1, 10):
                            clean_line = clean_line.replace(
                                f"{i}. ", "", 1
                            )  # Only replace first occurrence
                        key_visual_elements.append(clean_line)

            # Prioritize structured points if found, otherwise use full text
            if key_visual_elements:
                # We found numbered points - use them
                visual_summary = " ".join(key_visual_elements)

                full_context = f"""IMAGE ANALYSIS:
Primary Content: {key_visual_elements[0] if len(key_visual_elements) > 0 else "N/A"}
Visual Style: {key_visual_elements[1] if len(key_visual_elements) > 1 else "N/A"}
Details Visible: {key_visual_elements[2] if len(key_visual_elements) > 2 else "N/A"}
Search Context: {key_visual_elements[3] if len(key_visual_elements) > 3 else "N/A"}

FULL DESCRIPTION: {visual_summary}

SUMMARY: {context}
KEYWORDS: {keywords_str}"""
            elif image_desc:
                # No numbered points but have image description
                full_context = f"IMAGE CONTENT: {image_desc}\n\nSUMMARY: {context}\nKEYWORDS: {keywords_str}"
            else:
                # No image description at all
                full_context = f"SUMMARY: {context}\nKEYWORDS: {keywords_str}"

            prompt = f"""You are a file organization assistant. You MUST choose EXACTLY ONE category name from the available list.

FILE ANALYSIS:
{full_context}

AVAILABLE CATEGORIES (choose EXACTLY one of these):
{', '.join(category_names)}

CRITICAL RULES:
1. You MUST respond with EXACTLY ONE category name from the list above
2. DO NOT invent new category names
3. DO NOT combine categories
4. DO NOT add explanations to the category name
5. If unsure, pick the closest match from the available list
6. Only respond "NONE" if the content truly doesn't fit ANY available category

Examples of CORRECT responses:
CATEGORY: lecture
CATEGORY: Female
CATEGORY: black with white txt

Examples of INCORRECT responses (DO NOT DO THIS):
CATEGORY: Error Tutorials/Code Debugging  ❌ (not in list)
CATEGORY: Female (because...)  ❌ (no explanations)
CATEGORY: lecture, Female  ❌ (pick only one)

Respond in this EXACT format:
CATEGORY: <EXACT category name from available list, or NONE>
CONFIDENCE: <0-100>
REASONING: <why this matches>"""

            response = state.ollama_client.generate(model=PHI3_MODEL, prompt=prompt)

            output = response["response"]
            logger.debug(f"AI Classification response:\n{output}")

            # Parse AI response
            predicted_category = None
            ai_confidence = 0.0
            ai_reasoning = ""

            for line in output.split("\n"):
                if line.startswith("CATEGORY:"):
                    cat_str = line.replace("CATEGORY:", "").strip()
                    # Extract just the category name (before any parentheses or extra explanation)
                    if "(" in cat_str:
                        predicted_category = cat_str.split("(")[0].strip()
                    else:
                        predicted_category = cat_str
                elif line.startswith("CONFIDENCE:"):
                    try:
                        conf_str = line.replace("CONFIDENCE:", "").strip()
                        # Extract only the first number (handle "85" or "85%" or "85.5")
                        import re

                        match = re.search(r"(\d+\.?\d*)", conf_str)
                        if match:
                            conf_value = float(match.group(1))
                            # If value is > 100, it's probably already a percentage gone wrong
                            if conf_value > 100:
                                ai_confidence = 0.5  # Fallback
                            else:
                                ai_confidence = conf_value / 100.0
                        else:
                            ai_confidence = 0.5
                    except Exception as e:
                        logger.warning(f"Failed to parse confidence: {e}")
                        ai_confidence = 0.5
                elif line.startswith("REASONING:"):
                    ai_reasoning = line.replace("REASONING:", "").strip()

            # If AI said NONE or empty, return no match
            if not predicted_category or predicted_category.upper() == "NONE":
                print("\n" + "=" * 80)
                print("⚠️  AI RETURNED 'NONE' - NOT MATCHING ANY CATEGORY")
                print("=" * 80)
                print(f"AI's reasoning: {ai_reasoning}")
                print(f"Available categories: {', '.join(category_names)}")
                print("=" * 80 + "\n")
                return {"category": None, "confidence": 0.0}

            # Find best matching category from user's list
            best_match = None
            best_score = 0.0
            category_details = {}
            ai_picked_valid_category = False

            for cat in categories:
                # Check if AI's prediction matches this category
                cat_name_lower = cat["name"].lower()
                pred_lower = predicted_category.lower()

                if cat_name_lower in pred_lower or pred_lower in cat_name_lower:
                    # AI picked this category
                    ai_picked_valid_category = True
                    semantic_score, matched_points = (
                        AIProcessor._calculate_semantic_match(full_context, cat["name"])
                    )
                    combined_score = (ai_confidence * 0.6) + (semantic_score * 0.4)

                    category_details[cat["name"]] = {
                        "score": combined_score,
                        "ai_picked": True,
                        "ai_confidence": ai_confidence,
                        "semantic_match": semantic_score,
                        "matched_points": matched_points,
                        "reason": f"AI selected this. Confidence: {ai_confidence:.2%}, Semantic match: {semantic_score:.2%}",
                    }

                    if combined_score > best_score:
                        best_score = combined_score
                        best_match = cat["name"]
                else:
                    # AI did NOT pick this category
                    semantic_score, matched_points = (
                        AIProcessor._calculate_semantic_match(full_context, cat["name"])
                    )
                    penalty_score = semantic_score * 0.5

                    category_details[cat["name"]] = {
                        "score": penalty_score,
                        "ai_picked": False,
                        "ai_confidence": 0.0,
                        "semantic_match": semantic_score,
                        "matched_points": matched_points,
                        "reason": f"AI said '{predicted_category}', not this. Only semantic match: {semantic_score:.2%} × 0.5 penalty",
                    }

            # If AI picked a non-existent category, use the highest semantic match as fallback
            if not ai_picked_valid_category:
                print(f"\n⚠️  AI picked non-existent category: '{predicted_category}'")
                print(f"📌 Falling back to highest semantic match...")

                # Find category with highest score (even with penalty)
                for cat_name, details in category_details.items():
                    if details["score"] > best_score:
                        best_score = details["score"]
                        best_match = cat_name
                        # Upgrade the details to show it's the fallback winner
                        details["ai_picked"] = "fallback"

            # Print detailed breakdown for ALL categories
            print("\n" + "=" * 80)
            print("📊 DETAILED CLASSIFICATION BREAKDOWN")
            print("=" * 80)

            # Show what the AI analyzed (the numbered points)
            print(f"DEBUG: image_desc exists: {bool(image_desc)}")
            print(f"DEBUG: key_visual_elements count: {len(key_visual_elements)}")
            if image_desc:
                print(f"DEBUG: First 200 chars of image_desc: {image_desc[:200]}")

            if key_visual_elements:
                print("🔍 IMAGE ANALYSIS POINTS EXTRACTED:")
                for i, element in enumerate(key_visual_elements, 1):
                    print(f"   {i}. {element}")
                print("-" * 80)
            else:
                print("⚠️  No numbered points found in image description")
                if image_desc:
                    print(f"📝 Raw image description preview: {image_desc[:300]}...")
                print("-" * 80)

            print(f"🤖 AI Prediction: '{predicted_category}'")
            print(f"💭 AI Reasoning: {ai_reasoning}")
            print(f"🎯 AI Base Confidence: {ai_confidence:.2%}")
            print("-" * 80)

            # Sort categories by score
            sorted_cats = sorted(
                category_details.items(), key=lambda x: x[1]["score"], reverse=True
            )

            for cat_name, details in sorted_cats:
                score = details["score"]
                bar_length = int(score * 30)
                bar = "█" * bar_length + "░" * (30 - bar_length)

                print(f"\n📁 {cat_name}")
                print(f"   {bar} {score:.2%}")

                if details["ai_picked"]:
                    print(f"   ✅ AI PICKED THIS CATEGORY")
                    print(f"      • AI Confidence: {details['ai_confidence']:.2%}")
                    print(f"      • Semantic Match: {details['semantic_match']:.2%}")
                    if "matched_points" in details and details["matched_points"]:
                        print(
                            f"      • Matched in: {', '.join(details['matched_points'])}"
                        )
                    print(
                        f"      • Formula: (60% × {details['ai_confidence']:.2%}) + (40% × {details['semantic_match']:.2%})"
                    )
                    print(f"      • Final Score: {score:.2%}")
                else:
                    print(f"   ❌ AI DID NOT PICK THIS")
                    print(f"      • AI said: '{predicted_category}'")
                    print(f"      • Semantic Match: {details['semantic_match']:.2%}")
                    if "matched_points" in details and details["matched_points"]:
                        print(
                            f"      • Found in: {', '.join(details['matched_points'])}"
                        )
                    print(f"      • Penalty Applied: × 0.5")
                    print(f"      • Final Score: {score:.2%}")

                print(f"   📝 {details['reason']}")

            print("\n" + "=" * 80)
            print(
                f"🏆 WINNER: {best_match if best_match else 'NONE'} with {best_score:.2%}"
            )
            print(f"⚖️  Threshold: 30.00%")

            if best_match and best_score >= 0.30:
                print(f"✅ PASSED - File will be moved to '{best_match}'")
            elif best_match:
                print(f"❌ FAILED - Score {best_score:.2%} is below 30% threshold")
                print(f"📂 File will stay in temp_uploads")
                best_match = None
                best_score = 0.0
            else:
                print(f"❌ NO MATCH - All scores too low or AI said NONE")

            print("=" * 80 + "\n")

            # Apply confidence thresholds
            if best_match:
                if best_score < 0.30:
                    logger.debug(f"Score too low ({best_score:.2f}), rejecting match")
                    return {"category": None, "confidence": 0.0}

                best_score = min(best_score, 0.95)
                logger.info(
                    f"Classified as '{best_match}' with confidence {best_score:.2%}"
                )
                return {"category": best_match, "confidence": best_score}

            return {"category": None, "confidence": 0.0}

        except Exception as e:
            logger.error(f"Classification error: {e}")
            import traceback

            traceback.print_exc()
            return {"category": None, "confidence": 0.0}
