from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Dùng SQLite cho dễ ở giai đoạn phát triển
SQLALCHEMY_DATABASE_URL = "sqlite:///./rag_system.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# CHÍNH LÀ DÒNG NÀY ĐANG BỊ THIẾU TRONG MÁY CỦA BẠN (Nhớ viết hoa chữ B)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()