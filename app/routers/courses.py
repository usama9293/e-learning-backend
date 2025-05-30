from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Course, StudentCourse, TutorCourse, User, TutorInfo
from ..schemas import (
    CourseCreate, 
    CourseResponse, 
    TutorCourseResponse,
    TutorCourseWithDetails
)
from ..auth import get_current_user, role_required

router = APIRouter(
    prefix="/api/v1/courses",
    tags=["courses"]
)

# ... existing code ...

@router.post("/{course_id}/enroll", status_code=status.HTTP_200_OK)
async def enroll_in_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user is a student
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can enroll in courses"
        )
    
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if student is already enrolled
    existing_enrollment = db.query(StudentCourse).filter(
        StudentCourse.student_id == current_user.id,
        StudentCourse.course_id == course_id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )
    
    # Create enrollment
    enrollment = StudentCourse(
        student_id=current_user.id,
        course_id=course_id
    )
    
    try:
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        return {"message": "Successfully enrolled in course"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enroll in course"
        )

@router.post("/{course_id}/assign-tutor/{tutor_id}", response_model=TutorCourseResponse)
async def assign_tutor_to_course(
    course_id: int,
    tutor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if current user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can assign tutors to courses"
        )
    
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if tutor exists and is actually a tutor
    tutor = db.query(User).filter(User.id == tutor_id, User.role == "tutor").first()
    if not tutor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor not found"
        )
    
    # Check if tutor is already assigned to this course
    existing_assignment = db.query(TutorCourse).filter(
        TutorCourse.tutor_id == tutor_id,
        TutorCourse.course_id == course_id
    ).first()
    
    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tutor is already assigned to this course"
        )
    
    # Create tutor-course assignment
    assignment = TutorCourse(
        tutor_id=tutor_id,
        course_id=course_id
    )
    
    try:
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign tutor to course"
        )

@router.get("/{course_id}/tutors", response_model=List[TutorCourseWithDetails])
async def get_course_tutors(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Get all tutors assigned to this course with their details
    tutor_assignments = db.query(TutorCourse).filter(
        TutorCourse.course_id == course_id
    ).all()
    
    result = []
    for assignment in tutor_assignments:
        tutor = db.query(User).filter(User.id == assignment.tutor_id).first()
        tutor_info = db.query(TutorInfo).filter(TutorInfo.user_id == tutor.id).first()
        
        if tutor and tutor_info:
            result.append({
                "id": assignment.id,
                "tutor_id": tutor.id,
                "course_id": course_id,
                "assigned_date": assignment.assigned_date,
                "tutor": {
                    "id": tutor.id,
                    "email": tutor.email,
                    "first_name": tutor_info.first_name,
                    "last_name": tutor_info.last_name,
                    "specialization": tutor_info.specialization,
                    "experience_years": tutor_info.experience_years,
                    "bio": tutor_info.bio
                },
                "course": {
                    "id": course.id,
                    "name": course.name,
                    "description": course.description,
                    "schedule_date": course.schedule_date,
                    "schedule_time": course.schedule_time
                }
            })
    
    return result

@router.get("/tutor/{tutor_id}/courses", response_model=List[TutorCourseWithDetails])
async def get_tutor_courses(
    tutor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if tutor exists
    tutor = db.query(User).filter(User.id == tutor_id, User.role == "tutor").first()
    if not tutor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor not found"
        )
    
    # Get all courses assigned to this tutor
    tutor_assignments = db.query(TutorCourse).filter(
        TutorCourse.tutor_id == tutor_id
    ).all()
    
    result = []
    for assignment in tutor_assignments:
        course = db.query(Course).filter(Course.id == assignment.course_id).first()
        tutor_info = db.query(TutorInfo).filter(TutorInfo.user_id == tutor.id).first()
        
        if course and tutor_info:
            result.append({
                "id": assignment.id,
                "tutor_id": tutor_id,
                "course_id": course.id,
                "assigned_date": assignment.assigned_date,
                "tutor": {
                    "id": tutor.id,
                    "email": tutor.email,
                    "first_name": tutor_info.first_name,
                    "last_name": tutor_info.last_name,
                    "specialization": tutor_info.specialization,
                    "experience_years": tutor_info.experience_years,
                    "bio": tutor_info.bio
                },
                "course": {
                    "id": course.id,
                    "name": course.name,
                    "description": course.description,
                    "schedule_date": course.schedule_date,
                    "schedule_time": course.schedule_time
                }
            })
    
    return result 