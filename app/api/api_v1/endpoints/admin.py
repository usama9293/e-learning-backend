from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from app.schemas.user import UserOut, UserCreate, UserUpdate
from app.schemas.course import CourseOut, CourseCreate, CourseUpdate
from app.schemas.session import SessionOut
from app.schemas.payment import PaymentOut
from app.schemas.log import LogOut
from app.models.user import User, UserRole, StudentInfo, TutorInfo
from app.models.course import Course
from app.models.session import Session as SessionModel
from app.models.payment import Payment
from app.models.log import Log
from app.api.api_v1.deps import get_db, roles_required, get_current_user
from app.core.cache import cache
from app.core.pagination import PaginationParams, PaginatedResponse
from datetime import datetime
from fastapi_pagination import Page, add_pagination, paginate
from fastapi import FastAPI, Query, Depends, Response
from sqlalchemy import select
from app.models.user import TutorInfo,User
from app.models.settings import SystemSettings
from app.core.create_log import create_log


from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Optional


from app.schemas.admin import DashboardStats, RecentActivity, EnrollmentTrend



router = APIRouter()

# Define a dependency function that returns the pagination parameters
def get_pagination_params(
    # page must be greater than 0
    page: int = Query(1, gt=0),
    # per_page must be greater than 0
    per_page: int = Query(10, gt=0)
):
    return {"page": page, "per_page": per_page}




@router.get("/admin/users", response_model=PaginatedResponse[UserOut])
# @cache(expire=300)
async def list_users(
    response: Response,
    pagination: PaginationParams = Depends(),
    search=Query(None),
    role=Query(None),
    is_active=Query(None),
    db: Session = Depends(get_db),
    sort_by: Optional[str] = Query(None, description="Sort by field (name, email, created_at)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)")
):
    # Get the page and per_page values from the pagination dictionary
    page = pagination.page
    per_page = pagination.per_page

    # Calculate the start and end indices for slicing the items list
    start = (page - 1) * per_page
    end = start + per_page
    query = db.query(User).filter(User.role != "admin")

    if search:
        query = query.filter(
            (User.full_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if sort_by:
        sort_column = getattr(User, sort_by, User.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)
   
    
    total = query.count()
    
    # # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) *per_page
    
    # # Get paginated items
    items = query.offset(offset).limit(per_page).all()
    
    return {"items": items, "total": total, "page": page, "per_page": per_page, "total_pages": total_pages}



@router.get("/admin/users/tutors", response_model=PaginatedResponse[UserOut])
# @cache(expire=300)
async def list_tutors(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    search: Optional[str] = None
):
    query = db.query(User).filter(User.role == "tutor")
    
    if search:
        query = query.filter(
            (User.full_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    
    total = query.count()
    
    # # Calculate pagination
    page = pagination.page
    per_page = pagination.per_page
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) *per_page
    
    # # Get paginated items
    items = query.offset(offset).limit(per_page).all()
    
    return {"items": items, "total": total, "page": page, "per_page": per_page, "total_pages": total_pages}


@router.post("/admin/users", response_model=UserOut)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create users")
    
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=user.password,  # Hash in real app!
        role=user.role,
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        create_log(db, "User created", new_user.email)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create user")

@router.put("/admin/users/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update users")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    try:
        db.commit()
        db.refresh(user)
        create_log(db, "User updated", user.email)
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update user")

@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete users")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        db.delete(user)
        db.commit()
        create_log(db, "User deleted", user.email)
        return {"detail": "User deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete user")

# COURSES
@router.get("/admin/courses", response_model=PaginatedResponse[CourseOut])
# @cache(expire=300)
async def list_courses(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    search: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: Optional[str] = Query(None, description="Sort by field (title, created_at)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)")
):
    query = db.query(Course)
    
    if search:
        query = query.filter(
            (Course.name.ilike(f"%{search}%")) |
            (Course.description.ilike(f"%{search}%"))
        )
    
    if status:
        query = query.filter(Course.status == status)
    
    if sort_by:
        sort_column = getattr(Course, sort_by, Course.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)
    
    total = query.count()
    
    # # Calculate pagination
    page = pagination.page
    per_page = pagination.per_page
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) *per_page
    
    # # Get paginated items
    items = query.offset(offset).limit(per_page).all()
    
    return {"items": items, "total": total, "page": page, "per_page": per_page, "total_pages": total_pages}

    
    return paginate(query, pagination)

@router.post("/admin/courses", response_model=CourseOut)
async def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create courses")
    
    new_course = Course(
        **course.dict(),
        # created_by=current_user.id,
        created_at=datetime.utcnow()
    )
    
    try:
        db.add(new_course)
        db.commit()
        db.refresh(new_course)
        create_log(db, "Course created", new_course.name)
        return new_course
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create course")

@router.put("/admin/courses/{course_id}", response_model=CourseOut)
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update courses")
    
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    for field, value in course_update.dict(exclude_unset=True).items():
        
        setattr(course, field, value)
    
    try:
        db.commit()
        db.refresh(course)
        create_log(db, "Course updated", course.name)
        return course
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update course")

@router.delete("/admin/courses/{course_id}")
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete courses")
    
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    try:
        db.delete(course)
        db.commit()
        create_log(db, "Course deleted", course.name)
        return {"detail": "Course deleted"}
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete course")

# SESSIONS
@router.get("/admin/sessions", response_model=PaginatedResponse[SessionOut])
# @cache(expire=300)
async def list_sessions(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = db.query(SessionModel)
   
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
    # for item in items:
    #     # user = db.query(User).filter(User.id == item.tutor_info_id).first()
      
    #     # tutor = db.query(TutorInfo).filter(TutorInfo.user_id == item.tutor_info_id).first()
    #     item.full_name = item.tutor.full_name
    #     # print(item.tutor)
    
    return {"items": items, "total": total, "page": page, "per_page": per_page, "total_pages": total_pages}


# PAYMENTS
@router.get("/admin/payments", response_model=PaginatedResponse[PaymentOut])
# @cache(expire=300)
async def list_payments(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = db.query(Payment)
    
    if status:
        query = query.filter(Payment.status == status)
    
    if start_date:
        query = query.filter(Payment.created_at >= start_date)
    
    if end_date:
        query = query.filter(Payment.created_at <= end_date)
    
    total = query.count()
    
    # # Calculate pagination
    page = pagination.page
    per_page = pagination.per_page
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) *per_page
    
    # # Get paginated items
    items = query.offset(offset).limit(per_page).all()
    
    
    return {"items": items, "total": total, "page": page, "per_page": per_page, "total_pages": total_pages}

# LOGS
@router.get("/admin/logs", response_model=PaginatedResponse[LogOut])
# @cache(expire=300)
async def list_logs(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = db.query(Log)
    
    if action:
        query = query.filter(Log.action == action)
    
    if start_date:
        query = query.filter(Log.created_at >= start_date)
    
    if end_date:
        query = query.filter(Log.created_at <= end_date)
    
    total = query.count()
    
    # # Calculate pagination
    page = pagination.page
    per_page = pagination.per_page
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) *per_page
    
    # # Get paginated items
    items = query.offset(offset).limit(per_page).all()
  
    
    return {"items": items, "total": total, "page": page, "per_page": per_page, "total_pages": total_pages}

@router.get("/admin/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can access this resource")
    try:
        # Get total counts
        total_students = db.query(func.count(StudentInfo.id)).scalar()
        total_tutors = db.query(func.count(TutorInfo.id)).scalar()
        total_courses = db.query(func.count(Course.id)).scalar()
        total_sessions = db.query(func.count(SessionModel.id)).scalar()

        # Get recent activities (last 10 activities)
        recent_activities = []
        
        # Get recent course creations
        recent_courses = db.query(Course).order_by(desc(Course.created_at)).limit(5).all()
        for course in recent_courses:
            recent_activities.append({
                "id": course.id,
                "type": "course",
                "description": f"New course created: {course.name}",
                "timestamp": course.created_at.isoformat()
            })

        # Get recent session creations
        recent_sessions = db.query(SessionModel).order_by(desc(SessionModel.created_at)).limit(5).all()
        for session in recent_sessions:
            recent_activities.append({
                "id": session.id,
                "type": "session",
                "description": f"New session scheduled for {session.date}",
                "timestamp": session.created_at.isoformat()
            })

        # Sort activities by timestamp and get the most recent 10
        # recent_activities.sort(key=lambda x: x["timestamp"], reverse=True)
        recent_activities = recent_activities[:10]

        # Get enrollment trend (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        enrollment_trend = []
        
        # Get daily student registrations
        daily_registrations = db.query(
            func.date(StudentInfo.dob).label('date'),
            func.count(StudentInfo.id).label('count')
        ).filter(
            StudentInfo.dob >= thirty_days_ago
        ).group_by(
            func.date(StudentInfo.dob)
        ).all()

        # Convert to the required format
        enrollment_trend = [
            {"date": str(reg.date), "count": reg.count}
            for reg in daily_registrations
        ]

        return {
            "totalStudents": total_students,
            "totalTutors": total_tutors,
            "totalCourses": total_courses,
            "totalSessions": total_sessions,
            "recentActivity": recent_activities,
            "enrollmentTrend": enrollment_trend
        }

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)) 