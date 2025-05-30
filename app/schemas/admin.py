from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RecentActivity(BaseModel):
    id: int
    type: str
    description: str
    timestamp: str

class EnrollmentTrend(BaseModel):
    date: str
    count: int

class DashboardStats(BaseModel):
    totalStudents: int
    totalTutors: int
    totalCourses: int
    totalSessions: int
    recentActivity: List[RecentActivity]
    enrollmentTrend: List[EnrollmentTrend]

    class Config:
        from_attributes = True 