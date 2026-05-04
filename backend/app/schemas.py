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
    
    @field_validator('password')
    @classmethod
    def password_must_be_valid(cls, v: str) -> str:
        # Kiểm tra độ dài password
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        if len(v) > 128:
            raise ValueError('Password must be less than 128 characters')
        return v

# Khuôn mẫu dành riêng cho Đăng nhập (Vì giao diện Sign In chỉ cần Email + Pass)
class UserLogin(BaseModel):
    email: EmailStr
    password: str   

# Khuôn mẫu trả về khi người dùng đăng nhập thành công (chứa token JWT) 
class Token(BaseModel):
    access_token: str
    token_type: str

# Khuôn mẫu để thay đổi mật khẩu
class ChangePassword(BaseModel):
    current_password: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def new_password_must_be_valid(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('New password must be at least 6 characters')
        if len(v) > 128:
            raise ValueError('New password must be less than 128 characters')
        return v
