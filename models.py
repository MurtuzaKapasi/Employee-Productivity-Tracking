from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    profile_picture = db.Column(db.LargeBinary)  

class LoginLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    login_time = db.Column(db.DateTime, nullable=False)
    logout_time = db.Column(db.DateTime)
    total_working_hours = db.Column(db.Float)
    status = db.Column(db.String(50), nullable=False)

class EmployeeTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)


class MeetingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    meeting_start_time = db.Column(db.DateTime, nullable=False)
    meeting_end_time = db.Column(db.DateTime)
    meeting_with = db.Column(db.String(100))
    meeting_desc = db.Column(db.String(200))
    per_meeting_hours = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=False)

class BreakLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    break_time = db.Column(db.Float)
    break_category = db.Column(db.String(100))

class LunchBreakLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    lunch_duration = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=False)

class RecordingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_recording_time = db.Column(db.DateTime, nullable=False)
    end_recording_time = db.Column(db.DateTime)
    total_capture_time = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=False)


class MobileLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    mobile_usage_time = db.Column(db.Float)
    mobile_usage_category = db.Column(db.String(100))