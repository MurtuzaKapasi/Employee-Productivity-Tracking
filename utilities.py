from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from models import BreakLog, EmployeeTracking, MeetingLog, MobileLog, RecordingLog, User, LoginLog
from datetime import datetime
from flask import jsonify, session
from models import db


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
    login_time = log_entry.login_time
    total_working_hours = (logout_time - login_time).total_seconds() / 60.0
    if log_entry:
        log_entry.logout_time = logout_time
        log_entry.total_working_hours = total_working_hours
        log_entry.status = 'inactive'
        db.session.commit()

def fetch_employees():
    return EmployeeTracking.query.all()

def fetch_departments_count():
    return EmployeeTracking.query.distinct(EmployeeTracking.department).count()

def fetch_active_employees_count():
    return LoginLog.query.filter_by(status='active').count()

def log_start_recording(employee_id):
    emp = User.query.filter_by(id=employee_id).first()
    login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Use a proper datetime format
    # Create a new log entry
    track_entry = RecordingLog(
        employee_id=employee_id,
        start_recording_time=login_time,
        is_active=True
    )
    db.session.add(track_entry)
    db.session.commit()
    
    session['recording_log_id'] = track_entry.id
    
def log_stop_recording():
    recording_log_id = session.get('recording_log_id')
    if recording_log_id:
            recording_log = RecordingLog.query.get(recording_log_id)
            if recording_log:
                end_time = datetime.now()
                total_capture_time = (end_time - recording_log.start_recording_time).total_seconds() / 60.0

                recording_log.end_recording_time = end_time
                recording_log.total_capture_time = total_capture_time
                # recording_log.mobile_usage_time = phone_usage_time
                recording_log.is_active = False
                db.session.commit()
                
                session.pop('recording_log_id', None)  # Remove recording ID from session
            else:
                print("No active recording log found to stop.")
                

# Helper function to log employee data upon logout
def log_employee_logout(employee_id):
    try:
        # Get current time
        current_time = datetime.now()

        # Fetch the employee details from the User table
        user = User.query.filter_by(id=employee_id).first()

        if not user:
            return jsonify({'message': 'Employee not found', 'status': 'failure'})

        # Fetch today's login log entry from the LoginLog table for this employee
        login_log = LoginLog.query.filter_by(user_id=employee_id).order_by(LoginLog.login_time.desc()).first()

        if not login_log:
            return jsonify({'message': 'Login log not found for today', 'status': 'failure'})

        # Retrieve login_time, logout_time (if already set), and total_working_hours (if calculated)
        login_time = login_log.login_time
        logout_time = current_time
        total_working_hours = (current_time - login_time).total_seconds() / 60  # In minutes

        print(f"Login time: {login_time}, Logout time: {logout_time}, Total working hours: {total_working_hours}")
        # Fetch total recording time from RecordingLog for today
        total_recording_time = db.session.query(func.sum(RecordingLog.total_capture_time))\
            .filter(RecordingLog.employee_id == employee_id, RecordingLog.start_recording_time >= login_time).scalar() or 0
        print(f"Total recording time: {total_recording_time}")

        # Fetch total break time and number of breaks from BreakLog for today
        total_break_time = db.session.query(func.sum(BreakLog.break_time))\
            .filter(BreakLog.employee_id == employee_id, BreakLog.start_time >= login_time).scalar() or 0
        no_of_breaks = db.session.query(func.count(BreakLog.id))\
            .filter(BreakLog.employee_id == employee_id, BreakLog.start_time >= login_time).scalar() or 0
        print(f"Total break time: {total_break_time}, Number of breaks: {no_of_breaks}")

        # Fetch total mobile usage time and number of phone usages from MobileLog for today
        total_mobile_usage_time = db.session.query(func.sum(MobileLog.mobile_usage_time))\
            .filter(MobileLog.employee_id == employee_id, MobileLog.start_time >= login_time).scalar() or 0
        no_of_mobile_used = db.session.query(func.count(MobileLog.id))\
            .filter(MobileLog.employee_id == employee_id, MobileLog.start_time >= login_time).scalar() or 0
        print(f"Total mobile usage time: {total_mobile_usage_time}, Number of mobile usages: {no_of_mobile_used}")

        # Fetch total meeting time and number of meetings from MeetingLog for today
        total_meeting_time = db.session.query(func.sum(MeetingLog.per_meeting_hours))\
            .filter(MeetingLog.employee_id == employee_id, MeetingLog.meeting_start_time >= login_time).scalar() or 0
        no_of_meetings = db.session.query(func.count(MeetingLog.id))\
            .filter(MeetingLog.employee_id == employee_id, MeetingLog.meeting_start_time >= login_time).scalar() or 0
        print(f"Total meeting time: {total_meeting_time}, Number of meetings: {no_of_meetings}")

        # Calculate total present time and productivity score
        total_present_time = total_recording_time + total_meeting_time - total_break_time - total_mobile_usage_time
        total_distraction_time = total_break_time + total_mobile_usage_time
        print(f"Total present time: {total_present_time}, Total distraction time: {total_distraction_time}")

        # Avoid division by zero in productivity score calculation
        if total_distraction_time > 0:
            productivity_score = total_present_time / total_distraction_time
        else:
            productivity_score = 1.0  # Assume perfect productivity if no distractions occurred

        # Update or create the EmployeeTracking log with user details
        employee_tracking = EmployeeTracking(
            employee_id=employee_id,
            name=user.user_name,  # Use the name from User model
            department=user.department,  # Fetch department from User model
            position=user.position,  # Fetch position from User model
            login_time=login_time,  # Taken from LoginLog table
            logout_time=logout_time,  # Current time
            total_working_hours=total_working_hours,  # Calculate working hours in minutes
            total_recording_time=total_recording_time,
            total_break_time=total_break_time,
            no_of_breaks=no_of_breaks,
            total_mobile_usage_time=total_mobile_usage_time,
            no_of_mobile_used=no_of_mobile_used,
            total_meeting_time=total_meeting_time,
            no_of_meetings=no_of_meetings,
            total_present_time=total_present_time,
            productivity_score=productivity_score
        )

        # Add the entry to the session and commit
        db.session.add(employee_tracking)
        db.session.commit()

        # Update the LoginLog with logout time and total working hours
        login_log.logout_time = current_time
        login_log.total_working_hours = total_working_hours
        db.session.commit()

        return jsonify({'message': 'Employee tracking data logged successfully!', 'status': 'success'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e), 'status': 'failure'})