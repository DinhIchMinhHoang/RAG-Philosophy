from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import auth, documents, chat

# Tự động tạo file database SQLite (nếu chưa có)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lumina RAG Backend")

# Cấu hình CORS để Frontend (chạy ở Live Server) có thể gọi API mà không bị chặn
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Trong môi trường production thì thay bằng URL của frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn các API từ file routers vào app chính
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "Chào mừng đến hệ thống Lumina RAG"}