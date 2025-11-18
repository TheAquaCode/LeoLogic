"""
BART-MNLI Classifier for File Organization
Fast zero-shot classification to replace Phi3-Mini classification

NEW FILE: Backend/file_organizer/bart_classifier.py
"""

from transformers import pipeline
from typing import Dict, List
import torch
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BARTClassifier:
    """
    Fast file classification using BART-MNLI
    Replaces Phi3-Mini for category classification
    """
    
    def __init__(self):
        logger.info("🚀 Loading BART-MNLI classifier...")
        
        try:
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )
            logger.info("✅ BART-MNLI loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load BART-MNLI: {e}")
            raise
    
    def prepare_text(self, analysis: Dict, filename: str = "") -> str:
        """
        Build classification text from Phi3's analysis
        
        Args:
            analysis: Dict from AIProcessor.analyze_content()
            filename: Fallback filename if analysis is empty
        
        Returns:
            Formatted text for BART classification (never empty)
        """
        parts = []
        
        # 1. Summary (most important)
        summary = analysis.get('summary', '').strip()
        if summary:
            parts.append(summary)
        
        # 2. Keywords (high signal)
        keywords = analysis.get('keywords', [])
        if keywords:
            parts.append(f"Keywords: {', '.join(keywords)}")
        
        # 3. Image description
        img_desc = analysis.get('image_description', '').strip()
        if img_desc:
            # Extract first few key points
            lines = [l.strip() for l in img_desc.split('\n') if l.strip()]
            key_points = []
            for line in lines[:3]:
                # Remove numbering
                clean = line
                for i in range(1, 10):
                    clean = clean.replace(f"{i}. ", "")
                if len(clean) > 10:
                    key_points.append(clean)
            
            if key_points:
                parts.append("Visual: " + ". ".join(key_points))
        
        # 4. Category suggestions (can help)
        suggestions = analysis.get('category_suggestions', [])
        if suggestions:
            parts.append(f"Themes: {', '.join(suggestions[:2])}")
        
        # Combine
        text = ". ".join(parts).strip()
        
        # CRITICAL: If still empty, use filename as last resort
        if not text:
            logger.warning(f"Empty analysis! Using filename as fallback: {filename}")
            # Extract useful info from filename
            if filename:
                # Remove extension and path
                from pathlib import Path
                name = Path(filename).stem
                # Replace underscores/hyphens with spaces
                name = name.replace('_', ' ').replace('-', ' ')
                text = f"File named: {name}"
            else:
                text = "Unknown file content"
        
        # Truncate to BART's limit (512 tokens ≈ 2000 chars)
        max_chars = 2000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        return text
    
    def classify(self, analysis: Dict, categories: List[Dict], filename: str = "") -> Dict:
        """
        Classify file into one of the given categories
        
        Args:
            analysis: Output from AIProcessor.analyze_content()
            categories: List of category dicts with 'name' key
            filename: Filename for fallback if analysis is empty
        
        Returns:
            {"category": str, "confidence": float}
        """
        # Validate categories
        if not categories or len(categories) == 0:
            logger.error("❌ No categories provided for classification!")
            logger.error("   Please create categories in File Explorer before processing files.")
            return {"category": None, "confidence": 0.0}
        
        # Prepare text (NEVER returns empty string)
        text = self.prepare_text(analysis, filename)
        
        # Prepare category names
        category_names = [c['name'] for c in categories if c.get('name')]
        
        # Validate category names
        if not category_names or len(category_names) == 0:
            logger.error("❌ Categories have no names!")
            return {"category": None, "confidence": 0.0}
        
        logger.debug(f"Classifying with BART...")
        logger.debug(f"  Text ({len(text)} chars): {text[:150]}...")
        logger.debug(f"  Categories ({len(category_names)}): {category_names}")
        
        try:
            # Run classification
            result = self.classifier(
                text,
                candidate_labels=category_names,
                multi_label=False,
                hypothesis_template="This file contains content about {}."
            )
            
            # Get results
            top_category = result['labels'][0]
            top_confidence = result['scores'][0]
            
            # Detailed logging
            print("\n" + "="*80)
            print("📊 BART CLASSIFICATION")
            print("="*80)
            print(f"Input text: {text[:100]}...")
            print(f"\nScores:")
            for i, (label, score) in enumerate(zip(result['labels'][:5], result['scores'][:5])):
                bar = "█" * int(score * 30)
                marker = "👉" if i == 0 else "  "
                print(f"{marker} {label:20s} {bar:30s} {score:.2%}")
            print(f"\n🎯 Selected: {top_category} ({top_confidence:.2%})")
            print("="*80 + "\n")
            
            return {
                "category": top_category,
                "confidence": top_confidence
            }
            
        except Exception as e:
            logger.error(f"❌ BART classification failed: {e}")
            logger.error(f"   Text was: '{text}'")
            logger.error(f"   Categories were: {category_names}")
            import traceback
            traceback.print_exc()
            return {"category": None, "confidence": 0.0}


class BARTBatchClassifier:
    """
    Batch processing version for multiple files
    Much faster when processing folders
    """
    
    def __init__(self, batch_size: int = 8):
        logger.info(f"🚀 Loading BART-MNLI with batch size {batch_size}...")
        
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0 if torch.cuda.is_available() else -1,
            batch_size=batch_size
        )
        self.batch_size = batch_size
        logger.info("✅ Batch classifier ready")
    
    def classify_batch(
        self, 
        analyses: List[Dict], 
        categories: List[Dict],
        filenames: List[str] = None
    ) -> List[Dict]:
        """
        Classify multiple files at once
        
        Args:
            analyses: List of analysis dicts from AIProcessor
            categories: List of category dicts
            filenames: Optional list of filenames for fallback
        
        Returns:
            List of {"category": str, "confidence": float}
        """
        if not categories or not analyses:
            return [{"category": None, "confidence": 0.0}] * len(analyses)
        
        category_names = [c['name'] for c in categories if c.get('name')]
        
        if not category_names:
            return [{"category": None, "confidence": 0.0}] * len(analyses)
        
        # Prepare texts
        single_classifier = BARTClassifier()
        texts = []
        for i, a in enumerate(analyses):
            filename = filenames[i] if filenames and i < len(filenames) else ""
            text = single_classifier.prepare_text(a, filename)
            texts.append(text)
        
        logger.info(f"🚀 Batch classifying {len(texts)} files...")
        
        # Classify all
        results = []
        for text in texts:
            try:
                result = self.classifier(
                    text,
                    candidate_labels=category_names,
                    multi_label=False,
                    hypothesis_template="This file contains content about {}."
                )
                
                results.append({
                    "category": result['labels'][0],
                    "confidence": result['scores'][0]
                })
            except Exception as e:
                logger.error(f"Batch classification error: {e}")
                results.append({"category": None, "confidence": 0.0})
        
        logger.info(f"✅ Batch classification complete")
        return results