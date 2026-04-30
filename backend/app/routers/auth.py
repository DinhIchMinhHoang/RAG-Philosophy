from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..core import security

# Dependency để lấy user hiện tại từ token
def get_current_user(authorization: str = Header(None), db: Session = Depends(database.get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )
    
    token = authorization[7:]  # Bỏ "Bearer " prefix
    username = security.decode_access_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return db_user

# Tạo một "nhóm" API chuyên xử lý vấn đề xác thực
router = APIRouter(tags=["Authentication"])

# API ĐĂNG KÝ
@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=schemas.Token)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # 1. Kiểm tra xem Email này đã có ai dùng chưa
    db_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email đã được sử dụng, vui lòng chọn email khác!")

    # 1.2 Kiểm tra xem Username này đã có ai dùng chưa
    db_username = db.query(models.User).filter(models.User.username == user.username).first()
    if db_username:
        raise HTTPException(status_code=400, detail="User name đã tồn tại, vui lòng chọn tên khác!")
    
    # 2. Băm mật khẩu
    hashed_password = security.get_password_hash(user.password)
    
    # 3. Tạo user mới và lưu vào DB
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)    # Đưa vào hàng chờ
    db.commit() 
    db.refresh(new_user)    # cập nhật thông tin mới nhất (id) cho new_user
    
    # 4. Tạo token để tự động đăng nhập sau khi signup
    access_token = security.create_access_token(subject=new_user.username)
    
    return {"access_token": access_token, "token_type": "bearer"}

# API DĂNG NHẬP
@router.post("/login", status_code=status.HTTP_200_OK, response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(database.get_db)):
    # 1. Tìm user trong Database
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    
    # 2. Kiểm tra user có tồn tại không và mật khẩu có đúng không
    if not db_user or not security.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai email hoặc mật khẩu!",
        )
    
    # 3. Nếu đúng hết, tạo vé thông hành JWT (tấm thẻ sẽ chứa định danh người dùng)
    access_token = security.create_access_token(subject=db_user.username)
    
    return {"access_token": access_token, "token_type": "bearer"}

# API THAY ĐỔI MẬT KHẨU
@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    change_pwd: schemas.ChangePassword,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    # 1. Kiểm tra mật khẩu hiện tại có đúng không
    if not security.verify_password(change_pwd.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect!",
        )
    
    # 2. Kiểm tra mật khẩu mới không được giống mật khẩu cũ
    if change_pwd.current_password == change_pwd.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password!",
        )
    
    # 3. Băm mật khẩu mới
    hashed_new_password = security.get_password_hash(change_pwd.new_password)
    
    # 4. Cập nhật mật khẩu trong database
    current_user.hashed_password = hashed_new_password
    db.add(current_user)
    db.commit()
    
    return {"message": "Password changed successfully!"}