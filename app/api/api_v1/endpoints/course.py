from fastapi import APIRouter, Depends, HTTPException,status
from typing import List
from sqlalchemy.orm import Session
from app.schemas.course import CourseOut, CourseCreate, CourseUpdate
from app.schemas.session import SessionOut
from app.schemas.user import StudentInfoOut
from app.schemas.tutor import TutorOut as TutorInfoOut
from app.models.course import Course, CourseStudent, CourseTutor
from app.models.session import Session as SessionModel
from app.api.api_v1.deps import get_db, roles_required, get_current_user
from app.models.user import User, StudentInfo, TutorInfo
from app.core.create_log import create_log
router = APIRouter()

@router.get("/courses", response_model=List[CourseOut], dependencies=[Depends(roles_required('student', 'tutor', 'admin'))])
def list_courses(db: Session = Depends(get_db), user:User=Depends(get_current_user)):
    enrolled= [] 
    if user.role == 'student':
        course = user.student_info.courses
        enrolled = [x.id for x in user.student_info.courses]
        print(enrolled)
        for c in course:
            print(c.name)
        
    courses = db.query(Course).filter(~Course.id.in_(enrolled)).all()
    return courses

@router.post("/courses", response_model=CourseOut, dependencies=[Depends(roles_required('admin'))])
def create_course(course: CourseCreate, db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    new_course = Course(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    create_log(db,"Course Created", current_user.email)
    return new_course

@router.get("/courses/{course_id}", response_model=CourseOut, dependencies=[Depends(roles_required('student', 'tutor', 'admin'))])
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.put("/courses/{course_id}", response_model=CourseOut, dependencies=[Depends(roles_required('admin'))])
def update_course(course_id: int, course_update: CourseUpdate, db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    for field, value in course_update.dict(exclude_unset=True).items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    create_log(db,"Course Update", current_user.email)
    return course

@router.delete("/courses/{course_id}", dependencies=[Depends(roles_required('admin'))])
def delete_course(course_id: int, db: Session = Depends(get_db),current_user:User=Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
    create_log(db,"Course Deleted", current_user.email)
    return {"detail": "Course deleted"}




@router.get('/courses/{course_id}/sessions', response_model=List[SessionOut])
def get_course_sessions(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    sessions = db.query(SessionModel).filter(SessionModel.course_id == course_id).all()
    for s in sessions:
        s.full_name = s.tutor.full_name
    return sessions

@router.get("/courses/{course_id}/students", response_model=List[StudentInfoOut])
def get_course_students(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course.students

@router.get("/courses/{course_id}/tutors", response_model=List[TutorInfoOut])
def get_course_tutors(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course.tutors

@router.get("/courses/{course_id}/enroll", status_code=status.HTTP_200_OK,dependencies=[Depends(roles_required('student'))])
def check_enrollment(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    return {"enrolled":course in current_user.student_info.courses}


