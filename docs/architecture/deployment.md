# Deployment

## Current Environment

### Development Setup

```bash
# 1. Install dependencies
python -m pip install -r requirements.txt

# 2. Create .env file
GEMINI_API_KEY=your_key_here
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=60

# 3. Start backend
uvicorn backend.app.main:app --reload --port 8000

# 4. Start frontend (static files)
# Use VS Code Live Server or any static file server
# Serve frontend/index.html
```

## Production Considerations

### Backend

1. **Change CORS**:
   ```python
   # backend/app/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend.com"],  # Restrict
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Set Secret Key**:
   ```bash
   export SECRET_KEY=$(openssl rand -hex 32)
   ```

3. **Use Persistent Qdrant**:
   ```python
   # rag_core/config.py
   QDRANT_LOCATION: str = "http://localhost:6333"  # Or file path
   ```

4. **Production Server**: Use gunicorn with workers
   ```bash
   gunicorn backend.app.main:app --workers 4 --bind 0.0.0.0:8000
   ```

### Frontend

1. **Build**: No build step needed (static files)
2. **Host**: Any static hosting (nginx, S3, Vercel)
3. **Update BASE_URL**: Change API.BASE_URL to production backend URL

### Ollama (for OCR)

- Requires Ollama running: `ollama serve`
- Model: glm-ocr
- Port: 11434 (default)

## Docker (Future)

No Docker configuration currently. Potential setup:

```dockerfile
# Dockerfile
FROM python:3.10
# ... install deps, copy files
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0"]
```