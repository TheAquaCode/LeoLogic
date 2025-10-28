"""
AI Model Initialization
"""

from transformers import pipeline
from config.settings import BART_MODEL_NAME
from .state import state


def initialize_models():
    """Load BART model for classification"""
    print("🔄 Loading BART model for classification...")
    state.bart_classifier = pipeline("zero-shot-classification", model=BART_MODEL_NAME)
    state.is_initialized = True
    print("✅ BART model loaded")
