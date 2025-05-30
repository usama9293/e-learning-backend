from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.schemas.tutor import TutorOut, TutorCreate, TutorUpdate
from app.schemas.course import CourseOut,TutorCourseOut
from app.schemas.session import SessionOut
from app.schemas.material import MaterialOut
from app.models.user import User, TutorInfo, StudentInfo
from app.models.course import Course, CourseTutor
from app.models.session import Session as SessionModel
from app.api.api_v1.deps import get_db, roles_required, get_current_user
from app.core.cache import cache
from app.core.pagination import PaginationParams, paginate, PaginatedResponse
from app.models.material import Material
from app.models.assignment import Assignment
from app.models.chat import Chat
from app.schemas.chat import ChatOut
from app.schemas.assignment import AssignmentOut
from app.schemas.student import StudentOut
from datetime import datetime
router = APIRouter()

@router.get("/tutors", response_model=List[TutorOut])
@cache(expire=300)
async def list_tutors(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    search: Optional[str] = None,
    sort_by: Optional[str] = Query(None, description="Sort by field (name, created_at)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)")
):
    query = db.query(TutorInfo)
    
    if search:
        query = query.filter(
            (TutorInfo.full_name.ilike(f"%{search}%")) |
            (TutorInfo.email.ilike(f"%{search}%"))
        )
    
    if sort_by:
        sort_column = getattr(TutorInfo, sort_by, TutorInfo.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)
    
    return paginate(query, pagination)

@router.get("/tutors/{tutor_id}", response_model=TutorOut)
@cache(expire=300)
async def get_tutor(
    tutor_id: int,
    db: Session = Depends(get_db)
):
    tutor = db.query(TutorInfo).filter(TutorInfo.id == tutor_id).first()
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return tutor

@router.get("/tutor/courses", response_model=PaginatedResponse[TutorCourseOut])
# @cache(expire=300)
async def get_tutor_courses(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    user:User = Depends(get_current_user),
    search: Optional[str] = None,
):
    if user.role != 'tutor':
        return HTTPException(404, detail="Login as tutor")
    print(user.tutor_info.id,user.tutor_info.full_name)
    print(user.tutor_info.courses)
    courses = user.tutor_info.courses
    for item in courses:
        item.enrolled = len(item.students)

    total = len(courses)
    
    # # Calculate pagination
    page = pagination.page
    per_page = pagination.per_page
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) *per_page
    print(courses)
 
    
   
    return {"items": courses, "total": total, "page": page, "per_page": per_page, "total_pages": total_pages}

@router.get("/tutor/courses/{course_id}", response_model=TutorCourseOut)
# @cache(expire=300)
async def get_tutor_courses(
    course_id:int,
    db: Session = Depends(get_db),
    user:User = Depends(get_current_user),
    search: Optional[str] = None,
):
    if user.role != 'tutor':
        print(user.role)
        return HTTPException(404, detail="Login as tutor")
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        print(course)
        raise HTTPException(404, detail="Course not found")
    course.enrolled = len(course.students)

   
    
   
    return course
@router.get("/tutor/courses/{course_id}/materials", response_model=PaginatedResponse[MaterialOut])
# @cache(expire=300)
async def get_tutor_materials(
    course_id:int = 0,
    db: Session = Depends(get_db),
    page:int=1,
    per_page:int=10,
    user:User = Depends(get_current_user)
):
    print(course_id,page,per_page)
    if user.role != 'tutor':
        return HTTPException(404, detail="Login as tutor")
    materials = db.query(Material).filter(Material.course_id == course_id and Material.tutor_info_id == user.tutor_info.id).all()
    total = len(materials)
    
    # # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) *per_page
    
   
    return {"items": materials, "total": total, "page": page, "per_page": per_page, "total_pages": total_pages}

@router.get("/tutor/courses/{course_id}/assignments", response_model=PaginatedResponse[AssignmentOut])
# @cache(expire=300)
async def get_tutor_assignments(
    cuourse_id:int,
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    user:User = Depends(get_current_user)
):
    if user.role != 'tutor':
        return HTTPException(404, detail="Login as tutor")
    
    assignments = db.query(Assignment).filter(Assignment.course_id == cuourse_id and Assignment.tutor_info_id == user.tutor_info.id).all()
    total = len(assignments)
    
    # # Calculate pagination
    page = pagination.page
    per_page = pagination.per_page
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) *per_page
    
   
    return {"items": assignments, "total": total, "page": page, "per_page": per_page, "total_pages": total_pages}

@router.get("/tutor/courses/{course_id}/students", response_model=PaginatedResponse[StudentOut])
# @cache(expire=300)
async def get_tutor_students(
    cuourse_id:int,
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    user:User = Depends(get_current_user)
):
    if user.role != 'tutor':
        return HTTPException(404, detail="Login as tutor")
    course = db.query(Course).filter(Course.id == cuourse_id).first()
    if not course:
        return HTTPException(404, detail="Course not found")
    students = course.students
    total = len(students)
    
    # # Calculate pagination
    page = pagination.page
    per_page = pagination.per_page
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) *per_page
    
   
    return {"items": students, "total": total, "page": page, "per_page": per_page, "total_pages": total_pages}

@router.get("/tutor/courses/{course_id}/chats", response_model=PaginatedResponse[ChatOut])
async def get_tutor_chats(
    course_id:int,
    db: Session = Depends(get_db),
    user:User = Depends(get_current_user),
    page:int=1,
    per_page:int=10
):
    if user.role != 'tutor':
        return HTTPException(404, detail="Login as tutor")
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        return HTTPException(404, detail="Course not found")
    chats = course.chats
    total = len(chats)
    
    # # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) *per_page

    return {"items": chats, "total": total, "page": page, "per_page": per_page, "total_pages": total_pages}

@router.get("/tutors/{tutor_id}/sessions", response_model=List[SessionOut])
@cache(expire=300)
async def get_tutor_sessions(
    tutor_id: int,
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    status: Optional[str] = None
):
    tutor = db.query(TutorInfo).filter(TutorInfo.id == tutor_id).first()
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")
    
    query = db.query(SessionModel).filter(SessionModel.tutor_info_id == tutor_id)
    
    if status:
        query = query.filter(SessionModel.status == status)
    
    return query.all()

@router.get("/tutor/sessions", response_model=PaginatedResponse[SessionOut])
# @cache(expire=300)
async def list_sessions(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user :User=Depends(get_current_user)
):
    if user.role != 'tutor':
        return HTTPException(404, detail="Login as tutor")
    sessions = user.tutor_info.sessions
    query = db.query(SessionModel).filter(SessionModel.tutor_info_id == user.tutor_info.id)
   
    if status:
        query = query.filter(SessionModel.status == status)
    
    if start_date:
        query = query.filter(SessionModel.start_time >= start_date)
    
    if end_date:
        query = query.filter(SessionModel.end_time <= end_date)
    
    total = query.count()
    
    # # Calculate pagination
    page = pagination.page
    per_page = pagination.per_page
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) *per_page
    
    # # Get paginated items
    items = query.offset(offset).limit(per_page).all()
    items = sessions[offset:per_page]
    
    # for item in items:
    #     # user = db.query(User).filter(User.id == item.tutor_info_id).first()
    #     print(item.students)
    #     # tutor = db.query(TutorInfo).filter(TutorInfo.user_id == item.tutor_info_id).first()
      
    #     # print(item.tutor)
    
    return {"items": items, "total": total, "page": page, "per_page": per_page, "total_pages": total_pages}



@router.put("/tutors/{tutor_id}", response_model=TutorOut)
async def update_tutor(
    tutor_id: int,
    tutor_update: TutorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin" and current_user.id != tutor_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this tutor")
    
    tutor = db.query(TutorInfo).filter(TutorInfo.id == tutor_id).first()
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")
    
    for field, value in tutor_update.dict(exclude_unset=True).items():
        setattr(tutor, field, value)
    
    try:
        db.commit()
        db.refresh(tutor)
        return tutor
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update tutor")

@router.delete("/tutors/{tutor_id}")
async def delete_tutor(
    tutor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete tutors")
    
    tutor = db.query(TutorInfo).filter(TutorInfo.id == tutor_id).first()
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor not found")
    
    try:
        db.delete(tutor)
        db.commit()
        return {"detail": "Tutor deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete tutor")

