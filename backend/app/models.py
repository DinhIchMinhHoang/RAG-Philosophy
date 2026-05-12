from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class User(Base):
    __tablename__ = "users" # Tên bảng trong database sẽ là "users"

    id = Column(Integer, primary_key=True, index=True)              # cột id
    username = Column(String, unique=True, index=True, nullable=False)      # cột username
    email = Column(String, unique=True, index=True, nullable=False)     # cột email
    hashed_password = Column(String, nullable=False)            # cột hashed_password
    # Role flag for admin users. Default False for regular users.
    is_admin = Column(Boolean, default=False, nullable=False)
