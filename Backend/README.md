# Leologic Backend - Local AI Edition

AI-powered file organizer with local AI models (Ollama + Whisper) and RAG-enabled chatbot.

## 🚀 Quick Start

### 1. Install System Dependencies

**Ollama**: Visit https://ollama.ai  
**FFmpeg**: For video processing  
**Tesseract**: For OCR

### 2. Pull AI Models

```bash
ollama pull phi3:mini
ollama pull llava-phi3
```

### 3. Setup Python

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 4. Run

```bash
python main.py
```

Services start on:
- File Organizer: http://localhost:5001
- Chatbot: http://localhost:5000

See full documentation in the code!
