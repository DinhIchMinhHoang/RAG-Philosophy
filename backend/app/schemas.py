from pydantic import BaseModel, EmailStr, field_validator

# KhuÃ´n máº«u khi ngÆ°á»i dÃ¹ng gá»­i dá»¯ liá»‡u ÄÄƒng kÃ½ tá»« Frontend lÃªn
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator('email')
    @classmethod
    def email_must_be_allowed(cls, v: str) -> str:
        email = v.lower()
        if not (email.endswith('@gmail.com') or email.endswith('@lumina.com.vn')):
            raise ValueError('Há»‡ thá»‘ng chá»‰ cháº¥p nháº­n tÃ i khoáº£n @gmail.com hoáº·c @lumina.com.vn')
        return v

    @field_validator('password')
    @classmethod
    def password_must_be_valid(cls, v: str) -> str:
        # Kiá»ƒm tra Ä‘á»™ dÃ i password
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        if len(v) > 128:
            raise ValueError('Password must be less than 128 characters')
        return v

# KhuÃ´n máº«u dÃ nh riÃªng cho ÄÄƒng nháº­p (VÃ¬ giao diá»‡n Sign In chá»‰ cáº§n Email + Pass)
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# KhuÃ´n máº«u tráº£ vá» khi ngÆ°á»i dÃ¹ng Ä‘Äƒng nháº­p thÃ nh cÃ´ng (chá»©a token JWT)
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

# KhuÃ´n máº«u Ä‘á»ƒ thay Ä‘á»•i máº­t kháº©u
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
