from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Optional
from ..database import get_db
from ..models.user import User, UserRole
from ..models.course import Course
from ..models.session import Session as SessionModel
from ..models.student_info import StudentInfo
from ..models.tutor_info import TutorInfo
from ..schemas.admin import DashboardStats, RecentActivity, EnrollmentTrend
from ..auth import get_current_admin_user

router = APIRouter()

@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
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
        recent_activities.sort(key=lambda x: x["timestamp"], reverse=True)
        recent_activities = recent_activities[:10]

        # Get enrollment trend (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        enrollment_trend = []
        
        # Get daily student registrations
        daily_registrations = db.query(
            func.date(StudentInfo.created_at).label('date'),
            func.count(StudentInfo.id).label('count')
        ).filter(
            StudentInfo.created_at >= thirty_days_ago
        ).group_by(
            func.date(StudentInfo.created_at)
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
        raise HTTPException(status_code=500, detail=str(e)) 