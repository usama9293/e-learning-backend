from main import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import datetime, timedelta
from app.models.user import User, UserRole, StudentInfo, TutorInfo
from app.models.course import Course
from app.models.session import Session, SessionStudent
from app.models.material import Material
from app.models.event import Event
from app.core.create_log import create_log
from app.schemas.user import UserCreate
import random
from app.models.assignment import Assignment, AssignmentFile
db = next(get_db())

# add users
payload = {
  "email": "{}@example.com",
  "password": "user",
  "role": "tutor",
  "full_name": "TUTOR 1",
  "dob": "2020-10-10",
  "gender": "string",
  "contact_number": "string",
  "address": "string",
  "grade_level": "string",
  "emergency_contact": "string",
  "parent_guardian": "string"
}
admin = 0
    
def add_student():
    admin=0
    userN = 0
    tutor = 0
    
    for i in range(10):
        
        userN += 1
        tutor += 1
        
        
        for role in ['student','tutor','admin']:
            user = {k:v for k,v in payload.items()}
            user['role'] = role
            
            user['full_name'] = role.upper() +f' {userN}'
            if role in ['student','tutor']:
                user['email'] = user['email'].format(role+str(i))
                
            elif not admin and role == 'admin':
                user['email'] = user['email'].format('admin1')
                admin = 1
            else:
                continue 
            
            db_user = db.query(User).filter(User.email == user['email']).first()
            if db_user:
                print("Email already registered",db_user.email)
                continue
            new_user = User(
                full_name=user['full_name'],
                email=user['email'],
                hashed_password=get_password_hash(user['password']),
                role=user['role'],
                is_active=True
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Save info based on role
            if user['role'] == 'student':
                student_info = StudentInfo(
                    user_id=new_user.id,
                    full_name=user['full_name'],
                    dob= datetime.strptime(user['dob'], '%Y-%m-%d'),
                    gender=user['gender'],
                    contact_number=user['contact_number'],
                    address=user['address'],
                    grade_level=user['grade_level'],
                    emergency_contact=user['emergency_contact'],
                    parent_guardian=user['parent_guardian']
                )
                db.add(student_info)
            elif user['role'] == 'tutor':
                tutor_info = TutorInfo(
                    user_id=new_user.id,
                    full_name=user['full_name'],
                    dob=datetime.strptime(user['dob'], '%Y-%m-%d'),
                    gender=user['gender'],
                    contact_number=user['contact_number'],
                    address=user['address']
                )
                db.add(tutor_info)
            
            db.commit()
            
                
            
        
# add course


course_payload = {
  "name": "string",
  "description": "string",
  "image": "string"
}


def add_course():
    # Add 20 courses
    for i in range(20):
        course = Course(
            price=50,
            name=f"Course {i+1}",
            description=f"Description for Course {i+1}",
            image=f"https://www.bing.com/th/id/OIP.UtWTUYitM0tQB5mi2XeJdgAAAA?w=166&h=211&c=8&rs=1&qlt=90&o=6&pid=3.1&rm=2",
            created_at=datetime.utcnow(),
            # updated_at=datetime.utcnow()
        )
        db.add(course)
    db.commit()

events_payload = {
  "title": "string",
  "date": "string",
  "description": "string",
  "image": "string"
}
def add_event():
    # Add 10 events
    for i in range(10):
        event = Event(
            title=f"Event {i+1}",
            date=datetime.utcnow() + timedelta(days=i*7),  # Events spread over 10 weeks
            description=f"Description for Event {i+1}",
            image=f"https://www.bing.com/th/id/OIP.UtWTUYitM0tQB5mi2XeJdgAAAA?w=166&h=211&c=8&rs=1&qlt=90&o=6&pid=3.1&rm=2",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(event)
    db.commit()

materials_payload = {
  "course_id": 0,
  "name": "string",
  "file_path": "string"
}

def add_material():
    # Add materials for each course
    file = 'C:/Users/jam morada/Documents/university/README.md'
    sessions   = db.query(Session).all()
    for session in sessions:
        # Add 3 materials per course
        for i in range(3):
            material = Material(
                session_id=session.id,
                name=f"Material {i+1} for {session.title}",
                description=f"Description for Material {i+1}",
                file_path = file,
                link=file
                # created_at=datetime.utcnow(),
                # updated_at=datetime.utcnow()
            )
            db.add(material)
            
    db.commit()

def add_sessions():
    # Add sessions for each course
    courses = db.query(Course).all()
    tutors = db.query(TutorInfo).all()
    sessions = db.query(Session).all()
    for s in sessions:
        db.delete(s)
    for course in courses:
        # Assign random tutor to course
        tutor = random.choice(tutors)
        days = ['Mon','Tue','Wed','Thurs','Fri','Sat']
        # Add 5 sessions per course
        
        new_session = Session(
            course_id=course.id,
            tutor_info_id=tutor.id,
            title=f"Session for {course.name}",
            description=f"Description for Session",
            date=datetime.utcnow() ,  # Sessions spread over 5 weeks
            start_time=datetime.strptime("09:00","%H:%M").time(),
            end_time=datetime.strptime("10:00","%H:%M").time(),
            days = [random.choice(days)],
            # max_students=20,
            created_at=datetime.utcnow(),
            status = 'Scheduled'
            # updated_at=datetime.utcnow()
        )
        new_session.tutor = tutor
        tutor.courses .append(course)
        tutor.sessions.append(new_session)
        course.sessions.append(new_session)
        db.add(new_session)
    db.commit()

def add_assignments():
    sessions = db.query(Session).all()
    file = 'C:/Users/jam morada/Documents/university/README.md'
    for session in sessions:
        # Add 3 assignments per session
        for i in range(3):
            assignment = Assignment(
                session_id=session.id,
                title=f"Assignment {i+1} for {session.title}",
                description=f"Description for Assignment {i+1}",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                due_date = datetime(2020,7,10),
                total_points = 100
            )
            file_path = f"C:/Users/jam morada/Documents/university/README.md"
            assignment_file = AssignmentFile(
                assignment_id=assignment.id,
                file_path=file_path
            )
            db.add(assignment)
            db.add(assignment_file)
    db.commit()


def run_all_tests():
    print("Adding students and tutors...")
    add_student()
    print("Adding courses...")
    add_course()
    print("Adding events...")
    add_event()
    print("Adding materials...")
    add_material()
    print("Adding sessions...")
    add_sessions()
    print("Adding assignments...")
    add_assignments()
    print("All test data added successfully!")

if __name__ == "__main__":
    run_all_tests()