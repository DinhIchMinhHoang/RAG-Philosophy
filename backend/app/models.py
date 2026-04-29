from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users" # Tên bảng trong database sẽ là "users"

    id = Column(Integer, primary_key=True, index=True)              # cột id
    username = Column(String, unique=True, index=True, nullable=False)      # cột username
    email = Column(String, unique=True, index=True, nullable=False)     # cột email
    hashed_password = Column(String, nullable=False)            # cột hashed_password