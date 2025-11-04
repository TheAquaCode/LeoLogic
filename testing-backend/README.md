# Leologic Backend

AI-powered file organizer with intelligent categorization and chatbot assistance.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file:
```bash
cp .env.example .env
# Add your MISTRAL_API_KEY
```

3. Run the backend:
```bash
python main.py
```

## Services

- **File Organizer**: http://localhost:5001
- **Chatbot**: http://localhost:5000

## API Endpoints

### File Organizer (port 5001)
- `GET /api/health` - Health check
- `GET /api/watched-folders` - Get watched folders
- `POST /api/watched-folders` - Add watched folder
- `POST /api/watched-folders/<id>/toggle` - Toggle folder status
- `GET /api/categories` - Get categories
- `POST /api/categories` - Add category
- `POST /api/process-folder/<id>` - Process folder manually

### Chatbot (port 5000)
- `GET /health` - Health check
- `POST /chat` - Send message
- `POST /clear` - Clear history
- `GET /status` - Get status

## Structure

```
backend/
├── main.py                    # Entry point
├── config/                    # Configuration
├── file_organizer/           # File sorting service
├── chatbot/                  # Chatbot service
└── utils/                    # Utilities
```
