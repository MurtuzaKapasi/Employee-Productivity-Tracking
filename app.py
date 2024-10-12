from flask import Flask, redirect, request, jsonify, render_template
from config import Config
from models import db, EmployeeTracking
from datetime import datetime
import subprocess

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database with Flask
db.init_app(app)

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


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')


# manual login pages routes-----------------------
@app.route('/manual-login', methods=['GET', 'POST'])
def manual_login():
    if request.method == 'POST':
        # Handle the login form submission logic here
        username = request.form['username']
        password = request.form['password']
        # Check credentials and redirect or show error
        return redirect('/dashboard')  # Example redirection after successful login
    return render_template('manual_login.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        # Handle the admin login form submission
        username = request.form['username']
        password = request.form['password']
        # Check admin credentials and redirect to admin dashboard
        return redirect('/admin-dashboard')  # Example redirection for admins
    return render_template('admin_login.html')


# Admin dashboard routes-------------------------# Dummy function to fetch employees
def fetch_employees():
    # Return dummy employees data
    return dummy_employees

# Dummy function to fetch total departments count
def fetch_departments_count():
    # Assuming we have 4 departments for this example
    return 4

# Dummy function to fetch active employees count
def fetch_active_employees_count():
    # Let's assume we have 3 active employees for now
    return 3

# Admin Dashboard Route
@app.route('/admin-dashboard')
def admin_dashboard():
    # Fetch employee and department data
    employees = fetch_employees()  # Fetch dummy employees
    total_employees = len(employees)
    total_departments = fetch_departments_count()  # Fetch dummy departments count
    active_employees = fetch_active_employees_count()  # Fetch dummy active employees count
    inactive_employees = total_employees - active_employees

    return render_template('admin_dashboard.html', employees=employees, total_employees=total_employees,
                           total_departments=total_departments, active_employees=active_employees,
                           inactive_employees=inactive_employees)


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


# pending funcion ( need to perform database operation)
# @app.route('/employee-list')
# def employee_list():
#     employees = fetch_employees()  # Fetch all employees from the database
#     return render_template('employee_list.html', employees=employees)

@app.route('/statistics')
def statistics():
    # Code to fetch and display statistics, possibly from Power BI
    return render_template('statistics.html')



# Route to track employee absence and phone usage
@app.route('/track', methods=['POST'])
def track():
    data = request.json
    employee_id = data.get('employee_id')
    total_absent_time = data.get('total_absent_time')
    total_phone_usage_time = data.get('total_phone_usage_time')

    # Create a new tracking record in the database
    track_entry = EmployeeTracking(
        employee_id=employee_id,
        total_absent_time=total_absent_time,
        total_phone_usage_time=total_phone_usage_time,
    )

    db.session.add(track_entry)
    db.session.commit()

    return jsonify({'message': 'Data added successfully!'}), 201

# Route to start recording
@app.route('/start-recording', methods=['POST'])
def start_recording():
    try:
        # Run the employee_tracking.py file as a subprocess
        subprocess.Popen(['python', 'employee_tracker.py'], shell=True)  # Adjust path if necessary
        return jsonify({'message': 'Recording started successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to get tracking data for a specific employee
@app.route('/tracking-data/<employee_id>', methods=['GET'])
def get_tracking_data(employee_id):
    # Query the database for the latest tracking entry for the employee
    track_entry = EmployeeTracking.query.filter_by(employee_id=employee_id).order_by(EmployeeTracking.id.desc()).first()

    if track_entry:
        return jsonify({
            'total_absent_time': track_entry.total_absent_time,
            'total_phone_usage_time': track_entry.total_phone_usage_time
        }), 200
    else:
        return jsonify({'error': 'No tracking data found for this employee.'}), 404

if __name__ == '__main__':
    app.run(debug=True)