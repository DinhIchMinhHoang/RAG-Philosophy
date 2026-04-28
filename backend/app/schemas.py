from pydantic import BaseModel

# Schema dùng khi người dùng gửi thông tin Đăng ký / Đăng nhập
class UserCreate(BaseModel):
    username: str
    password: str

# Schema dùng để Backend trả Token về cho Frontend
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None