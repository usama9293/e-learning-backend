from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_v1.api import api_router
from app.core.security import get_password_hash
import os
from app.db.base import Base
from app.db.session import engine
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as aioredis
from app.models.user import User
from app.models.settings import SystemSettings
from app.db.session import get_db
db = next(get_db())
# from fastapi_pagination import Page, add_pagination, paginate
# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mathsmastery Institute API")
# add_pagination(app)
# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.include_router(api_router, prefix="/api/v1")

def add_admin():
    user = {
        "email": "admin@example.com",
        "password": "admin",
        "role": "admin",
        "full_name": "Admin 1",
        "dob": "2020-10-10",
        "gender": "string",
        "contact_number": "string",
        "address": "string",
        "grade_level": "string",
        "emergency_contact": "string",
        "parent_guardian": "string"
        }
    admin = db.query(User).filter(User.role=='admin').first()
    if not admin:
        admin = User(
                    full_name=user['full_name'],
                    email=user['email'],
                    hashed_password=get_password_hash(user['password']),
                    role=user['role'],
                    is_active=True
                )
        db.add(admin)
        db.commit()
@app.get("/")
def read_root():
    return {"message": "Welcome to the Mathsmastery Institute API!"}

@app.on_event("startup")
async def startup():
    # Initialize system settings
    add_admin()
    settings = SystemSettings(
        site_name="Maths Mastery Institute",
        site_description="Maths Mastery Institute",
        contact_email="admin@example.com",
        maintenance_mode=False)
    
    db.add(settings)
    db.commit()
    
    # Get Redis URL from environment variable or use default
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis = aioredis.from_url(redis_url, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

#cd e-learning-backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
# uvicorn main:app --reload --host 0.0.0.0 --port 8000
 # cd e-learning-frontend && npm run dev 