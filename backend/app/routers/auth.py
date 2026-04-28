from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..core import security

# Tạo một "nhóm" API chuyên xử lý vấn đề xác thực
router = APIRouter(tags=["Authentication"])

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # 1. Kiểm tra xem username đã có ai lấy chưa
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại, vui lòng chọn tên khác!")
    
    # 2. Băm mật khẩu
    hashed_password = security.get_password_hash(user.password)
    
    # 3. Tạo user mới và lưu vào DB
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Đăng ký thành công! Hãy tiến hành đăng nhập."}

@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # 1. Tìm user trong Database
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    
    # 2. Kiểm tra user có tồn tại không và mật khẩu có đúng không
    if not db_user or not security.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tài khoản hoặc mật khẩu!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Nếu đúng hết, tạo vé thông hành JWT
    access_token = security.create_access_token(subject=db_user.username)
    
    return {"access_token": access_token, "token_type": "bearer"}