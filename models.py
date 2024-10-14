from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100))

class LoginLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    login_time = db.Column(db.DateTime, nullable=False)
    logout_time = db.Column(db.DateTime)
    status = db.Column(db.String(50), nullable=False)

class EmployeeTracking(db.Model):
    employee_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    login_time = db.Column(db.String(10))
    logout_time = db.Column(db.String(10))
    total_hours_worked = db.Column(db.Integer)
    mobile_usage_minutes = db.Column(db.Integer)
    productive_hours = db.Column(db.Float)
    idle_time_hours = db.Column(db.Float)
    meetings_number = db.Column(db.Integer, default=0)
    meeting_hours = db.Column(db.Float, default=0.0)  
    meeting_info = db.Column(db.JSON) 
    class_of_breaks = db.Column(db.String(10)) 
    number_of_breaks = db.Column(db.Integer, default=0)  
    break_details = db.Column(db.JSON)  
    is_active = db.Column(db.Boolean, default=False)