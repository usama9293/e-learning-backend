from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserOut, StudentInfoCreate, TutorInfoCreate
from app.models.user import User, StudentInfo, TutorInfo
from app.api.api_v1.deps import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import datetime
from app.core.create_log import create_log
from app.schemas.auth import ChangePasswordRequest
from passlib.context import CryptContext
router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role=user.role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    create_log(db,"Assignment Created", user.email)
    
    # Save info based on role
    if user.role == 'student':
        student_info = StudentInfo(
            user_id=new_user.id,
            full_name=user.full_name,
            dob= datetime.strptime(user.dob, '%Y-%m-%d'),
            gender=user.gender,
            contact_number=user.contact_number,
            address=user.address,
            grade_level=user.grade_level,
            emergency_contact=user.emergency_contact,
            parent_guardian=user.parent_guardian
        )
        db.add(student_info)
    elif user.role == 'tutor':
        tutor_info = TutorInfo(
            user_id=new_user.id,
            full_name=user.full_name,
            dob=datetime.strptime(user.dob, '%Y-%m-%d'),
            gender=user.gender,
            contact_number=user.contact_number,
            address=user.address
        )
        db.add(tutor_info)
    
    db.commit()
    return new_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    create_log(db,action="Logged in", user_email=user.email)
    return {"access_token": access_token, "token_type": "bearer", "role": user.role.value, "user":user.to_dict()}

@router.post("/adminlogin")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role.value}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == data.userId).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not pwd_context.verify(data.currentPassword, user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    user.hashed_password = pwd_context.hash(data.newPassword)
    db.commit()

    return {"detail": "Password updated successfully"}
# @router.get("/me", response_model=UserOut)
# def get_me(current_user: User = Depends(...)):  # You will need a get_current_user dependency
#     return current_user 