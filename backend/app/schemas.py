from pydantic import BaseModel, EmailStr, field_validator

# Khuôn mẫu khi người dùng gửi dữ liệu Đăng ký từ Frontend lên
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator('email')
    @classmethod
    def email_must_be_allowed(cls, v: str) -> str:
        email = v.lower()
        if not (email.endswith('@gmail.com') or email.endswith('@lumina.com.vn')):
            raise ValueError('Hệ thống chỉ chấp nhận tài khoản @gmail.com hoặc @lumina.com.vn')
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


# Response model for user info (admin-facing)
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_admin: bool

    class Config:
        # Pydantic v2 uses `from_attributes` to allow orm object -> model conversion
        from_attributes = True

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


# Password reset schemas
class PasswordForgotRequest(BaseModel):
    email: EmailStr


class PasswordVerifyRequest(BaseModel):
    email: EmailStr
    code: str


class PasswordResetRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def new_password_must_be_valid(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('New password must be at least 6 characters')
        if len(v) > 128:
            raise ValueError('New password must be less than 128 characters')
        return v
