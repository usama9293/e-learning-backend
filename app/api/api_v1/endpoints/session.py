from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.schemas.session import SessionOut, SessionCreate, SessionUpdate
from app.schemas.user import StudentInfoOut
from app.schemas.tutor import TutorOut as TutorInfoOut
from app.models.session import Session as SessionModel, SessionStudent
from app.models.course import Course
from app.api.api_v1.deps import get_db, roles_required, get_current_user
from app.models.user import User, StudentInfo, TutorInfo
from app.schemas.user import TutorInfoCreate
from datetime import datetime
from sqlalchemy.orm import joinedload
router = APIRouter()

@router.get("/sessions", response_model=List[SessionOut])
def list_sessions(db: Session = Depends(get_db), user:User=Depends(get_current_user)):
    if user.role == 'student':
        sessions = user.student_info.sessions
    elif user.role == 'tutor':
        sessions = user.tutor_info.sessions
    else:
        sessions = db.query(SessionModel).all()
    for s in sessions:
        s.full_name = s.tutor.full_name
    return sessions

@router.post("/sessions", response_model=SessionOut)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    for key, value in session.dict().items():
        print(key, value)
    course = db.query(Course).filter(Course.id == session.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    print(session.tutor_info_id)
    tutor_info = db.query(TutorInfo).filter(TutorInfo.id == session.tutor_info_id).first()
   
    # user = db.query(User).filter(User.id==tutor_info.user_id).first()
    if not tutor_info:
        raise HTTPException(status_code=404, detail="Tutor not found")


    session.date = datetime.strptime(session.date, "%Y-%m-%d")
    session.start_time = datetime.strptime(session.start_time, "%H:%M").time()
    session.end_time = datetime.strptime(session.end_time, "%H:%M").time()

    new_session = SessionModel(**session.dict())
    print(new_session)
    db.add(new_session)
    db.commit()
    
    new_session.tutor = tutor_info
    tutor_info.courses .append(course)
    tutor_info.sessions.append(new_session)
    course.sessions.append(new_session)

   
    
    db.commit()
    db.refresh(new_session)
    
    # Re-query with relationships loaded
    new_session = db.query(SessionModel).options(
        joinedload(SessionModel.course),
        joinedload(SessionModel.tutor)
    ).get(new_session.id)

    # new_session.full_name = tutor_info.full_name
    

    return new_session



@router.get("/sessions/{session_id}/students", response_model=List[StudentInfoOut])
def get_session_students(session_id: int, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.students

@router.get("/sessions/{session_id}/tutor", response_model=TutorInfoCreate)
def get_session_tutor(session_id: int, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    print(session.tutor.user_id)
    print(session.tutor.id)
    print(session.tutor.user.email)
    return session.tutor

@router.post("/sessions/{session_id}/enroll", status_code=status.HTTP_200_OK)
async def enroll_in_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can enroll in sessions"
        )
    print(session_id)
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    course = db.query(Course).filter(Course.id == session.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    

    student_info = db.query(StudentInfo).filter(StudentInfo.user_id == current_user.id).first()
    if not student_info:
        raise HTTPException(status_code=404, detail="Student info not found")
    
    # Check if already enrolled
    existing_enrollment = db.query(SessionStudent).filter(
        SessionStudent.session_id == session_id,
        SessionStudent.student_id == student_info.id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(status_code=400, detail="Already enrolled in this session")
    
    # Create enrollment
    enrollment = SessionStudent(
        session_id=session_id,
        student_id=student_info.id,
        status="enrolled"
    )
    student_info.sessions.append(session)
    db.commit()
    db.refresh(student_info)

    course.students.append(student_info)
    db.commit()
    db.refresh(course)
    
    try:
        db.add(enrollment)
        db.commit()
        return {"message": "Successfully enrolled in session"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to enroll in session")

@router.post("/sessions/{session_id}/assign-tutor/{tutor_id}", status_code=status.HTTP_200_OK)
async def assign_tutor_to_session(
    session_id: int,
    tutor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can assign tutors")
    
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    tutor_info = db.query(TutorInfo).filter(TutorInfo.user_id == tutor_id).first()
    if not tutor_info:
        raise HTTPException(status_code=404, detail="Tutor not found")
    
    # Update session tutor
    session.tutor = tutor_info
    
    try:
        db.commit()
        return {"message": "Successfully assigned tutor to session"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to assign tutor to session")

@router.get("/sessions/{session_id}", response_model=SessionOut)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.put("/sessions/{session_id}", response_model=SessionOut)
def update_session(session_id:int, session_update:SessionUpdate, db: Session = Depends(get_db)):
    print(session_id,session_update)
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    for field, value in session_update.dict(exclude_unset=True).items():
        if 'time' in field:
            print(value)
            value = datetime.strptime(value,"%H:%M").time()
        if field == 'date':
            value = datetime.strptime(value,'%Y-%m-%d').date()
        setattr(session, field, value)
    db.commit()
    db.refresh(session)
    tutor = db.query(TutorInfo).filter(TutorInfo.user_id == session.tutor_info_id).first()
    session.full_name = tutor.full_name
    return session

@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"detail": "Session deleted"}
