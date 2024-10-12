import os

class Config:
    SECRET_KEY = 'mysecretkey'
    SQLALCHEMY_DATABASE_URI = 'postgresql://flask_user:Emp123@localhost/employee_tracking'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# CREATE USER flask_user WITH PASSWORD 'Emp123';

# GRANT ALL PRIVILEGES ON DATABASE employee_tracking TO flask_user;

# GRANT ALL PRIVILEGES ON SCHEMA public TO flask_user;

# python
# from app import app, db
# with app.app_context():
#     db.create_all()

