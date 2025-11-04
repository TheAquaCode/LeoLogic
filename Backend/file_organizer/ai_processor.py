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
            "entities": []
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
            
            response = state.ollama_client.generate(
                model=PHI3_MODEL,
                prompt=prompt
            )
            
            output = response['response']
            
            # Parse response
            result = {
                "summary": "",
                "keywords": [],
                "category_suggestions": []
            }
            
            for line in output.split('\n'):
                if line.startswith('SUMMARY:'):
                    result["summary"] = line.replace('SUMMARY:', '').strip()
                elif line.startswith('KEYWORDS:'):
                    keywords = line.replace('KEYWORDS:', '').strip()
                    result["keywords"] = [k.strip() for k in keywords.split(',')]
                elif line.startswith('CATEGORIES:'):
                    categories = line.replace('CATEGORIES:', '').strip()
                    result["category_suggestions"] = [c.strip() for c in categories.split(',')]
            
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
                images=[image_path]
            )
            
            return response['response']
            
        except Exception as e:
            logger.error(f"LLaVA-Phi3 error: {e}")
            return ""
    
    @staticmethod
    def classify_into_categories(analysis: Dict, categories: List[Dict]) -> Dict:
        """
        Use AI to classify into user-defined categories.
        Returns: {"category": str, "confidence": float}
        """
        if not categories or not state.ollama_client:
            return {"category": None, "confidence": 0.0}
        
        try:
            category_names = [c['name'] for c in categories]
            
            prompt = f"""Given this file analysis, which category fits best?

Summary: {analysis.get('summary', '')}
Keywords: {', '.join(analysis.get('keywords', []))}

Available categories: {', '.join(category_names)}

Respond with ONLY the category name that fits best."""
            
            response = state.ollama_client.generate(
                model=PHI3_MODEL,
                prompt=prompt
            )
            
            predicted_category = response['response'].strip()
            
            # Find best match
            for cat in categories:
                if cat['name'].lower() in predicted_category.lower():
                    return {"category": cat['name'], "confidence": 0.85}
            
            # Fallback to first suggestion
            if analysis.get('category_suggestions'):
                for suggestion in analysis['category_suggestions']:
                    for cat in categories:
                        if cat['name'].lower() in suggestion.lower():
                            return {"category": cat['name'], "confidence": 0.70}
            
            return {"category": None, "confidence": 0.0}
            
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return {"category": None, "confidence": 0.0}
