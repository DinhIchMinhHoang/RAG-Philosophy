from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Lấy đường dẫn tuyệt đối đến thư mục chứa file database.py (thư mục app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Lùi lại 1 cấp để ra thư mục backend và đặt file DB ở đó
DB_PATH = os.path.join(BASE_DIR, "..", "rag_system.db")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Dùng SQLite cho dễ ở giai đoạn phát triển
SQLALCHEMY_DATABASE_URL = "sqlite:///./rag_system.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()