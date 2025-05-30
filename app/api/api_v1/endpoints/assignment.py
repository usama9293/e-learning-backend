from fastapi import Form,APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.schemas.assignment import AssignmentOut, AssignmentCreate, AssignmentUpdate, SubmissionCreate, SubmissionOut
from app.models.assignment import Assignment, Submission,AssignmentFile
from app.models.user import User, StudentInfo
from app.models.course import Course
from app.api.api_v1.deps import get_db, roles_required, get_current_user
from app.core.cache import cache
from app.core.pagination import PaginationParams, paginate,PaginatedResponse
from app.core.storage import upload_file, delete_file
from datetime import datetime
from app.models.session import Session as SessionModel
import os
from app.core.create_log import create_log
router = APIRouter()

@router.get("/assignments/{session_id}", response_model=List[AssignmentOut])
# @cache(expire=300)
async def list_assignments(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    session_id: Optional[int] = None,
    status: Optional[str] = None,
    user:User=Depends(get_current_user)
):
    print(session_id)
    session = db.query(SessionModel).filter(SessionModel.id==session_id).first()
    if not session:
        return HTTPException(404,detail="Course not found")

    
    
    
    return session.assignments
@router.post("/assignments", response_model=AssignmentOut)
async def create_assignment(
    title: str = Form(...),
    description: str = Form(...),
    session_id: int = Form(...),
    due_date: str = Form(...),
    total_points: int = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file_url = None
    allowed = ['pdf', 'doc', 'docx', 'txt', 'zip', 'rar', 'jpg', 'jpeg', 'png']
    if file:
        filename = file.filename
        ext = os.path.splitext(filename)[1][1:].lower()  # get extension without dot
        if ext not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format: .{ext}. Allowed formats: {', '.join(allowed)}"
            )
        file_url = await upload_file(file, "assignments")
    if current_user.role not in ["admin", "tutor"]:
        raise HTTPException(status_code=403, detail="Only admins and tutors can create assignments")
    session = db.query(SessionModel).filter(SessionModel.id == int(session_id)).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

       
    
    assignment = Assignment(
        session_id=session.id,
        title=title,
        description=description,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        due_date = datetime(2020,7,10),
        total_points = total_points
    )
    
   
    
    try:
        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        assignment_file = AssignmentFile(
                assignment_id=assignment.id,
                file_path=file_url
            )
        db.add(assignment_file)
        db.commit()
        create_log(db,"Assignment Created", current_user.email)
        return assignment
    except Exception as e:
        print(e)
        if file_url:
            await delete_file(file_url)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create assignment")

@router.get("/assignments/{assignment_id}")
@cache(expire=300)
async def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment
@router.delete("/assignments/{assignment_id}")
async def update_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        return HTTPException(404,detail="Assignment not found")
    db.delete(assignment)
    db.commit()
    create_log(db,"Assignment Deleted", current_user.email)
    return {"detail":"deleted"}
    




@router.put("/assignments/{assignment_id}", response_model=AssignmentOut)
async def update_assignment(
    assignment_id: int,
    assignment_update: AssignmentUpdate,
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "tutor"]:
        raise HTTPException(status_code=403, detail="Only admins and tutors can update assignments")
    
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    old_file_url = assignment.file_url
    file_url = None
    
    if file:
        file_url = await upload_file(file, "assignments")
    
    for field, value in assignment_update.dict(exclude_unset=True).items():
        setattr(assignment, field, value)
    
    if file_url:
        assignment.file_url = file_url
    
    try:
        db.commit()
        db.refresh(assignment)
        if old_file_url and file_url:
            await delete_file(old_file_url)
        create_log(db,"Assignment Updated", current_user.email)
        return assignment
    except Exception as e:
        if file_url:
            await delete_file(file_url)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update assignment")

@router.post("/assignments/{assignment_id}/submit", response_model=SubmissionOut)
async def submit_assignment(
    assignment_id: int,
    content: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit assignments")
    
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    student_info = db.query(StudentInfo).filter(StudentInfo.user_id == current_user.id).first()
    if not student_info:
        raise HTTPException(status_code=404, detail="Student info not found")
    
    # Check if already submitted
    existing_submission = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.student_id == student_info.id
    ).first()
    
    if existing_submission:
        raise HTTPException(status_code=400, detail="Already submitted this assignment")
    
    # Save file and get URL
    file_url = await upload_file(file, "submissions")
    
    # Create submission data
    new_submission = Submission(
        assignment_id=assignment_id,
        student_id=student_info.id,
        file_url=file_url,
        content=content,
        submitted_at=datetime.utcnow()
    )
    
    try:
        db.add(new_submission)
        db.commit()
        db.refresh(new_submission)
        create_log(db,"Assignment Submitted", current_user.email)
        return new_submission
    except Exception as e:
        await delete_file(file_url)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to submit assignment")

@router.post("/assignments/{assignment_id}/grade/{submission_id}")
async def grade_submission(
    assignment_id: int,
    submission_id: int,
    grade: float,
    feedback: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "tutor"]:
        raise HTTPException(status_code=403, detail="Only admins and tutors can grade assignments")
    
    submission = db.query(Submission).filter(
        Submission.id == submission_id,
        Submission.assignment_id == assignment_id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    submission.grade = grade
    submission.feedback = feedback
    submission.graded_at = datetime.utcnow()
    submission.graded_by = current_user.id
    
    try:
        db.commit()
        db.refresh(submission)
        create_log(db,"Assignment Graded", current_user.email)
        return {"message": "Submission graded successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to grade submission")
