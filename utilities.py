from werkzeug.security import generate_password_hash, check_password_hash
from models import EmployeeTracking, User, LoginLog
from datetime import datetime
from flask import session
from models import db

dummy_employees_tracking = [
    {
        "employee_id": 1,
        "name": "John Doe",
        "department": "Testers",
        "position": "Junior Tester",
        "login_time": "09:00 AM",
        "logout_time": "05:00 PM",
        "total_hours_worked": 8,
        "breaks": {
            "number_of_breaks": 3,
            "breaks_details": [
                {"duration": 5, "type": "short"},
                {"duration": 7, "type": "medium"},
                {"duration": 15, "type": "long"}
            ]
        },
        "mobile_usage_minutes": 20,
        "meeting_hours": 1.5,
        "productive_hours": 5.5,
        "idle_time_hours": 1
    },
    {
        "employee_id": 2,
        "name": "Jane Smith",
        "department": "Developers",
        "position": "Senior Developer",
        "login_time": "10:00 AM",
        "logout_time": "06:00 PM",
        "total_hours_worked": 8,
        "breaks": {
            "number_of_breaks": 2,
            "breaks_details": [
                {"duration": 6, "type": "medium"},
                {"duration": 10, "type": "medium"}
            ]
        },
        "mobile_usage_minutes": 35,
        "meeting_hours": 2,
        "productive_hours": 5,
        "idle_time_hours": 1
    },
    {
        "employee_id": 3,
        "name": "Alice Johnson",
        "department": "Interns",
        "position": "Intern Developer",
        "login_time": "08:30 AM",
        "logout_time": "04:30 PM",
        "total_hours_worked": 8,
        "breaks": {
            "number_of_breaks": 4,
            "breaks_details": [
                {"duration": 3, "type": "short"},
                {"duration": 5, "type": "short"},
                {"duration": 8, "type": "medium"},
                {"duration": 12, "type": "long"}
            ]
        },
        "mobile_usage_minutes": 15,
        "meeting_hours": 0.5,
        "productive_hours": 6.5,
        "idle_time_hours": 1
    },
    {
        "employee_id": 4,
        "name": "Bob Lee",
        "department": "Project Managers",
        "position": "Project Manager",
        "login_time": "09:30 AM",
        "logout_time": "05:30 PM",
        "total_hours_worked": 8,
        "breaks": {
            "number_of_breaks": 1,
            "breaks_details": [
                {"duration": 10, "type": "medium"}
            ]
        },
        "mobile_usage_minutes": 5,
        "meeting_hours": 3,
        "productive_hours": 4,
        "idle_time_hours": 1
    },
    {
        "employee_id": 5,
        "name": "Eve Martinez",
        "department": "HR",
        "position": "HR Manager",
        "login_time": "08:45 AM",
        "logout_time": "04:45 PM",
        "total_hours_worked": 8,
        "breaks": {
            "number_of_breaks": 3,
            "breaks_details": [
                {"duration": 5, "type": "short"},
                {"duration": 6, "type": "short"},
                {"duration": 9, "type": "medium"}
            ]
        },
        "mobile_usage_minutes": 25,
        "meeting_hours": 1.8,
        "productive_hours": 5.2,
        "idle_time_hours": 1
    },
    {
        "employee_id": 6,
        "name": "Michael Brown",
        "department": "Developers",
        "position": "Junior Developer",
        "login_time": "09:15 AM",
        "logout_time": "05:15 PM",
        "total_hours_worked": 8,
        "breaks": {
            "number_of_breaks": 2,
            "breaks_details": [
                {"duration": 10, "type": "medium"},
                {"duration": 7, "type": "short"}
            ]
        },
        "mobile_usage_minutes": 45,
        "meeting_hours": 2.5,
        "productive_hours": 4.5,
        "idle_time_hours": 1
    },
    {
        "employee_id": 7,
        "name": "Laura White",
        "department": "Interns",
        "position": "Intern Tester",
        "login_time": "09:00 AM",
        "logout_time": "05:00 PM",
        "total_hours_worked": 8,
        "breaks": {
            "number_of_breaks": 4,
            "breaks_details": [
                {"duration": 3, "type": "short"},
                {"duration": 5, "type": "short"},
                {"duration": 12, "type": "long"},
                {"duration": 6, "type": "medium"}
            ]
        },
        "mobile_usage_minutes": 10,
        "meeting_hours": 0.7,
        "productive_hours": 6.3,
        "idle_time_hours": 1
    },
    {
        "employee_id": 8,
        "name": "David Green",
        "department": "Testers",
        "position": "Senior Tester",
        "login_time": "08:30 AM",
        "logout_time": "04:30 PM",
        "total_hours_worked": 8,
        "breaks": {
            "number_of_breaks": 3,
            "breaks_details": [
                {"duration": 7, "type": "medium"},
                {"duration": 5, "type": "short"},
                {"duration": 10, "type": "medium"}
            ]
        },
        "mobile_usage_minutes": 30,
        "meeting_hours": 2,
        "productive_hours": 5,
        "idle_time_hours": 1
    },
    {
        "employee_id": 9,
        "name": "Chris Lee",
        "department": "HR",
        "position": "HR Assistant",
        "login_time": "08:00 AM",
        "logout_time": "04:00 PM",
        "total_hours_worked": 8,
        "breaks": {
            "number_of_breaks": 2,
            "breaks_details": [
                {"duration": 8, "type": "medium"},
                {"duration": 5, "type": "short"}
            ]
        },
        "mobile_usage_minutes": 12,
        "meeting_hours": 1.5,
        "productive_hours": 5.5,
        "idle_time_hours": 1
    },
    {
        "employee_id": 10,
        "name": "Sophia Wilson",
        "department": "Developers",
        "position": "Junior Developer",
        "login_time": "09:45 AM",
        "logout_time": "05:45 PM",
        "total_hours_worked": 8,
        "breaks": {
            "number_of_breaks": 1,
            "breaks_details": [
                {"duration": 6, "type": "medium"}
            ]
        },
        "mobile_usage_minutes": 20,
        "meeting_hours": 1.2,
        "productive_hours": 5.8,
        "idle_time_hours": 1
    }
]


# Password hashing
def hash_password(password):
    return generate_password_hash(password)

def verify_password(stored_password, provided_password):
    # return check_password_hash(stored_password, provided_password)
    return provided_password == stored_password


def fetch_user_by_email(email):
    return User.query.filter_by(email=email).first()

# 1. User Registration
def register_employee(name, email, password, role, department=None):
    user = fetch_user_by_email(email)
    if user:
        return "Email already exists!"

    hashed_password = hash_password(password)

    new_user = User(
        user_name=name,
        email=email,
        password=password,
        role=role,
        department=department
    )
    db.session.add(new_user)
    db.session.commit()
    
    return "Employee registered successfully!"
# 2. User Login
def login_user(email, password):
    user = fetch_user_by_email(email)
    if not user:
        return "Invalid credentials"
    
    if verify_password(user.password, password):
        session['user_id'] = user.user_id
        session['role'] = user.role
        log_user_login(user.user_id)
        return "Login successful!"
    else:
        return "Invalid credentials"

def log_user_login(user_id):
    login_time = datetime.now()
    log_entry = LoginLog(user_id=user_id, login_time=login_time, status='active')
    db.session.add(log_entry)
    db.session.commit()

def log_user_logout(user_id):
    logout_time = datetime.now()
    log_entry = LoginLog.query.filter_by(user_id=user_id, status='active').first()
    if log_entry:
        log_entry.logout_time = logout_time
        log_entry.status = 'inactive'
        db.session.commit()

def fetch_employees():
    return EmployeeTracking.query.all()

def fetch_departments_count():
    return EmployeeTracking.query.distinct(EmployeeTracking.department).count()

def fetch_active_employees_count():
    return LoginLog.query.filter_by(status='active').count()
