from pydantic import BaseModel, EmailStr, field_validator

# Khuôn mẫu khi người dùng gửi dữ liệu Đăng ký từ Frontend lên
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator('email')
    @classmethod
    def email_must_be_gmail(cls, v: str) -> str:
        # Kiểm tra xem chuỗi email có kết thúc bằng @gmail.com hay không
        if not v.lower().endswith('@gmail.com'):
            # Nếu không phải, trả về lỗi để FastAPI báo lại cho Frontend
            raise ValueError('Hệ thống chỉ chấp nhận tài khoản @gmail.com')
        return v

# Khuôn mẫu dành riêng cho Đăng nhập (Vì giao diện Sign In chỉ cần Email + Pass)
class UserLogin(BaseModel):
    email: EmailStr
    password: str   

# Khuôn mẫu trả về khi người dùng đăng nhập thành công (chứa token JWT) 
class Token(BaseModel):
    access_token: str
    token_type: str