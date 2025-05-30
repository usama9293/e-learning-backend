from fastapi import APIRouter
from app.api.api_v1.endpoints import settings, auth, student, tutor, admin, user,assignment,course,payment,event,session,material

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(student.router, prefix="", tags=["students"])
api_router.include_router(tutor.router, prefix="", tags=["tutors"])
api_router.include_router(admin.router, prefix="", tags=["admin"])
api_router.include_router(user.router, prefix="", tags=["users"]) 
api_router.include_router(assignment.router, prefix="", tags=["assignments"])
api_router.include_router(course.router, prefix="", tags=["courses"])
api_router.include_router(payment.router, prefix="", tags=["payments"])
api_router.include_router(event.router, prefix="", tags=["events"])
api_router.include_router(session.router, prefix="", tags=["sessions"])
api_router.include_router(material.router, prefix="", tags=["materials"])
api_router.include_router(settings.router, prefix="", tags=["settings"])