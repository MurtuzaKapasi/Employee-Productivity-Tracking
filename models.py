from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class EmployeeTracking(db.Model):
    __tablename__ = 'tracking'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), nullable=False)
    total_absent_time = db.Column(db.Float, nullable=True)  # Store time in seconds
    total_phone_usage_time = db.Column(db.Float, nullable=True)  # Store time in seconds

    def __repr__(self):
        return f'<Employee {self.employee_id}>'
