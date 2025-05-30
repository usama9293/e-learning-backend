from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.schemas.payment import PaymentOut, PaymentCreate, PaymentUpdate
from app.models.payment import Payment
from app.models.user import User, StudentInfo
from app.models.course import Course
from app.api.api_v1.deps import get_db, roles_required, get_current_user
from app.core.cache import cache
from app.core.pagination import PaginationParams, paginate
from datetime import datetime

router = APIRouter()

@router.get("/payments", response_model=List[PaymentOut])
@cache(expire=300)
async def list_payments(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    student_id: Optional[int] = None,
    course_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = db.query(Payment)
    
    if student_id:
        query = query.filter(Payment.student_id == student_id)
    
    if course_id:
        query = query.filter(Payment.course_id == course_id)
    
    if status:
        query = query.filter(Payment.status == status)
    
    if start_date:
        query = query.filter(Payment.created_at >= start_date)
    
    if end_date:
        query = query.filter(Payment.created_at <= end_date)
    
    return paginate(query, pagination)

@router.post("/payments", response_model=PaymentOut)
async def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can create payments")
    
    student_info = db.query(StudentInfo).filter(StudentInfo.user_id == current_user.id).first()
    if not student_info:
        raise HTTPException(status_code=404, detail="Student info not found")
    
    course = db.query(Course).filter(Course.id == payment.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if payment already exists
    existing_payment = db.query(Payment).filter(
        Payment.student_id == student_info.id,
        Payment.course_id == payment.course_id,
        Payment.status.in_(["pending", "completed"])
    ).first()
    
    if existing_payment:
        raise HTTPException(status_code=400, detail="Payment already exists for this course")
    
    new_payment = Payment(
        **payment.dict(),
        student_id=student_info.id,
        status="pending",
        created_at=datetime.utcnow()
    )
    
    try:
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)
        return new_payment
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create payment")

@router.get("/payments/{payment_id}", response_model=PaymentOut)
@cache(expire=300)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if current_user.role != "admin" and payment.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this payment")
    
    return payment

@router.put("/payments/{payment_id}", response_model=PaymentOut)
async def update_payment(
    payment_id: int,
    payment_update: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update payments")
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.status == "completed":
        raise HTTPException(status_code=400, detail="Cannot update completed payment")
    
    for field, value in payment_update.dict(exclude_unset=True).items():
        setattr(payment, field, value)
    
    try:
        db.commit()
        db.refresh(payment)
        return payment
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update payment")

@router.post("/payments/{payment_id}/verify")
async def verify_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can verify payments")
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.status != "pending":
        raise HTTPException(status_code=400, detail="Payment is not pending")
    
    payment.status = "completed"
    payment.verified_at = datetime.utcnow()
    payment.verified_by = current_user.id
    
    try:
        db.commit()
        db.refresh(payment)
        return {"message": "Payment verified successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to verify payment")

@router.get("/payments/student/{student_id}/history", response_model=List[PaymentOut])
@cache(expire=300)
async def get_student_payment_history(
    student_id: int,
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Not authorized to view payment history")
    
    query = db.query(Payment).filter(Payment.student_id == student_id)
    return paginate(query, pagination)
