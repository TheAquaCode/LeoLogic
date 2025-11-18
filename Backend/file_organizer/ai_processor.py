"""
AI Processing with Ollama (Phi-3-Mini + LLaVA-Phi3)
Generic classification with BART-MNLI for fast category assignment

REPLACE FILE: Backend/file_organizer/ai_processor.py
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
    def classify_into_categories(analysis: Dict, categories: List[Dict], filename: str = "") -> Dict:
        """
        Classify content into user-defined categories using BART-MNLI.
        
        NEW: Uses BART-MNLI for fast zero-shot classification
        OLD: Used Phi3-Mini with complex semantic matching
        
        Args:
            analysis: Output from analyze_content()
            categories: List of category dicts with 'name' key
            filename: Filename for fallback if analysis is empty
        
        Returns: 
            {"category": str, "confidence": float}
        """
        if not categories:
            logger.error("ERROR: No categories provided!")
            logger.error("Create categories in File Explorer before processing files.")
            return {"category": None, "confidence": 0.0}
        
        if not state.bart_classifier:
            logger.error("ERROR: BART classifier not initialized!")
            logger.error("This should have been loaded on backend startup.")
            logger.error("Make sure models.py is calling initialize_models() which loads BART.")
            return {"category": None, "confidence": 0.0}

        try:
            # Use BART for classification (passes filename for fallback)
            result = state.bart_classifier.classify(analysis, categories, filename)
            
            if result.get('category'):
                logger.info(
                    f"SUCCESS: Classified as '{result['category']}' with confidence {result['confidence']:.2%}"
                )
            else:
                logger.warning(f"WARNING: Could not classify file")
            
            return result

        except Exception as e:
            logger.error(f"ERROR: Classification error: {e}")
            import traceback
            traceback.print_exc()
            return {"category": None, "confidence": 0.0}