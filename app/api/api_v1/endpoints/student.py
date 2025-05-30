from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.schemas.student import StudentOut, StudentCreate, StudentUpdate
from app.schemas.user import UserOut, UserUpdate,UserCreate,StudentInfoOut
from app.schemas.course import StudentCourseOut
from app.schemas.session import SessionStudentOut
from app.models.user import User, StudentInfo, TutorInfo
from app.models.course import Course, CourseStudent
from app.models.session import Session as SessionModel, SessionStudent
from app.api.api_v1.deps import get_db, roles_required, get_current_user
from app.core.cache import cache
from app.core.pagination import PaginationParams, paginate, PaginatedResponse



router = APIRouter()

@router.get("/students", response_model=List[StudentOut],dependencies=[Depends(roles_required('admin'))])
@cache(expire=300)  # Cache for 5 minutes
def list_students(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    search: Optional[str] = None,
    sort_by: Optional[str] = Query(None, description="Sort by field (name, created_at)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)")
):
   
    offset = (pagination.page - 1) * pagination.per_page
    query = db.query(StudentInfo).all()
    
    return query

#
@router.get("/students/courses", response_model=List[StudentCourseOut],dependencies=[Depends(roles_required('student'))])

async def get_student_courses(
    all_courses:bool=False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user = current_user.student_info
    courses = []
    if all_courses:
        enrolled = [x.id for x in current_user.courses]

        courses = db.query(Course).filter(~Course.id.in_(enrolled)).all()
        
    else:
        sessions = current_user.sessions
        s_ids = [x.id for x in sessions]
            
        
        for s in sessions:
            # s.full_name = s.tutor.full_name
            course = s.course
            course.tutor = s.tutor
            course.session=s
            courses.append(course)
    return courses

@router.get("/students/{student_id}courses", response_model=List[StudentCourseOut],dependencies=[Depends(roles_required('admin'))])

async def get_student_courses(
    student_id:int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    student = db.query(StudentInfo).filter(StudentInfo.id == student_id).first()
    if not student:
        return HTTPException(404, detail='Student not found')
    sessions = student.sessions
    s_ids = [x.id for x in sessions]
    courses = []
    
    for s in sessions:
        s.full_name = s.tutor.full_name
        course = s.course
        course.tutor = s.tutor
        course.session=s
        courses.append(course)
    return courses


@router.get("/students/{student_id}/sessions", response_model=List[SessionStudentOut],dependencies=[Depends(roles_required('student'))])

async def get_student_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    student = db.query(StudentInfo).filter(StudentInfo.id == current_user.student_info.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    r = [] 
    sessions = student.sessions.copy()
    for s in sessions:
        try:
            # s.full_name = s.tutor.full_name
            s.course.tutor = s.tutor
            s.course.session=s
        except Exception as e:
            print(e)
            r.append(s)
    for s in r:
        print(s)
        sessions.remove(s)

    db.commit()
        
    return sessions

@router.put("/students/{student_id}", response_model=StudentOut)
async def update_student(
    student_id: int,
    student_update: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this student")
    
    student = db.query(StudentInfo).filter(StudentInfo.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    for field, value in student_update.dict(exclude_unset=True).items():
        setattr(student, field, value)
    
    try:
        db.commit()
        db.refresh(student)
        return student
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update student")

@router.delete("/students/{student_id}", dependencies=[Depends(roles_required('student', 'admin'))])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return {"detail": "Student deleted"}



