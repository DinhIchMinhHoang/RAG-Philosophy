from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

# Lấy các biến cấu hình từ file .env
SECRET_KEY = os.getenv("SECRET_KEY", "khoa_du_phong_neu_quen_tao_env")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Cấu hình thuật toán băm mật khẩu (Argon2)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Kiểm tra xem pass người dùng nhập có khớp với pass trong DB không
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Băm mật khẩu ra chuỗi trước khi cất vào DB
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Tạo vé thông hành JWT
def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

# Giải mã token JWT để lấy username
def decode_access_token(token: str) -> Union[str, None]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None
