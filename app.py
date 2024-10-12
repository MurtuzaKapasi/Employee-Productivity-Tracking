from flask import Flask, redirect, request, jsonify, render_template, url_for
from config import Config
from models import LoginLog, User, db, EmployeeTracking
from datetime import datetime
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from routes import init_routes


app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database with Flask
db.init_app(app)

# Initialize routes
init_routes(app)


# -------------------------------------------------------------------------
@app.route('/add-employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        # Code to add employee to database
        return redirect('/admin-dashboard')
    return render_template('add_employee.html')

@app.route('/remove-employee', methods=['GET', 'POST'])
def remove_employee():
    if request.method == 'POST':
        # Code to remove employee from database
        return redirect('/admin-dashboard')
    return render_template('remove_employee.html')

@app.route('/add-section', methods=['GET', 'POST'])
def add_section():
    if request.method == 'POST':
        # Code to create a new department/section in the database
        return redirect('/admin-dashboard')
    return render_template('add_section.html')


@app.route('/statistics')
def statistics():
    # Code to fetch and display statistics, possibly from Power BI
    return render_template('statistics.html')

if __name__ == '__main__':
    app.run(debug=True)