# E-Learning Platform API

## Models Structure

### User Models
```python
class User:
    id: int
    full_name: str
    email: str
    hashed_password: str
    role: UserRole (student/tutor/admin)
    is_active: bool
    created_at: datetime
    student_info: StudentInfo (one-to-one)
    tutor_info: TutorInfo (one-to-one)

class StudentInfo:
    id: int
    user_id: int (FK to User)
    full_name: str
    dob: date
    gender: str
    contact_number: str
    address: str
    grade_level: str
    emergency_contact: str
    parent_guardian: str
    courses: List[Course] (many-to-many)
    sessions: List[Session] (many-to-many)

class TutorInfo:
    id: int
    user_id: int (FK to User)
    full_name: str
    dob: date
    gender: str
    contact_number: str
    address: str
    courses: List[Course] (many-to-many)
    sessions: List[Session] (one-to-many)
```

### Course Models
```python
class Course:
    id: int
    name: str
    description: str
    schedule_date: str
    schedule_time: str
    is_active: bool
    image: str
    created_at: datetime
    sessions: List[Session] (one-to-many)
    tutors: List[TutorInfo] (many-to-many)
    students: List[StudentInfo] (many-to-many)
    materials: List[Material] (one-to-many)
    assignments: List[Assignment] (one-to-many)

class CourseTutor:
    id: int
    course_id: int (FK to Course)
    tutor_id: int (FK to TutorInfo)
    created_at: datetime

class CourseStudent:
    id: int
    course_id: int (FK to Course)
    student_id: int (FK to StudentInfo)
    created_at: datetime
```

### Session Models
```python
class Session:
    id: int
    course_id: int (FK to Course)
    title: str
    description: str
    date: date
    time: time
    status: str
    created_at: datetime
    course: Course (many-to-one)
    tutor: TutorInfo (many-to-one)
    students: List[StudentInfo] (many-to-many)

class SessionStudent:
    id: int
    session_id: int (FK to Session)
    student_id: int (FK to StudentInfo)
    status: str
    created_at: datetime
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/register` - Register new user

### Courses
- `GET /api/v1/courses` - List all courses
- `POST /api/v1/courses` - Create new course (admin only)
- `GET /api/v1/courses/{course_id}` - Get course details
- `PUT /api/v1/courses/{course_id}` - Update course (admin only)
- `DELETE /api/v1/courses/{course_id}` - Delete course (admin only)
- `GET /api/v1/courses/{course_id}/sessions` - Get all sessions for a course
- `GET /api/v1/courses/{course_id}/students` - Get all students in a course
- `GET /api/v1/courses/{course_id}/tutors` - Get all tutors for a course
- `POST /api/v1/courses/{course_id}/enroll` - Enroll in a course (student only)
- `POST /api/v1/courses/{course_id}/assign-tutor/{tutor_id}` - Assign tutor to course (admin only)
- `GET /api/v1/tutor/courses` - Get all courses for a tutor

### Sessions
- `GET /api/v1/sessions` - List all sessions
- `POST /api/v1/sessions` - Create new session
- `GET /api/v1/sessions/{session_id}` - Get session details
- `PUT /api/v1/sessions/{session_id}` - Update session
- `DELETE /api/v1/sessions/{session_id}` - Delete session
- `GET /api/v1/sessions/{session_id}/students` - Get all students in a session
- `GET /api/v1/sessions/{session_id}/tutor` - Get tutor for a session
- `POST /api/v1/sessions/{session_id}/enroll` - Enroll in a session (student only)
- `POST /api/v1/sessions/{session_id}/assign-tutor/{tutor_id}` - Assign tutor to session (admin only)

### Users
- `GET /api/v1/users/me` - Get current user info
- `PUT /api/v1/users/me` - Update current user info
- `GET /api/v1/users/students` - List all students (admin only)
- `GET /api/v1/users/tutors` - List all tutors (admin only)

## Setup and Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run migrations:
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc` 