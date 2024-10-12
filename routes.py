import subprocess
from flask import request, render_template, session, redirect, url_for, jsonify
from utilities import fetch_active_employees_count, fetch_departments_count, fetch_employees, verify_password, fetch_user_by_email, hash_password, log_user_login, log_user_logout
from models import EmployeeTracking, User
from datetime import datetime


def init_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login')
    def login():
        return render_template('login.html')

    @app.route('/manual-login', methods=['GET', 'POST'])
    def manual_login():
        email = request.form['email']
        password = request.form['password']

        user = fetch_user_by_email(email)
        if not user or not verify_password(user.password, password):
            return "Invalid credentials!", 401

        session['user_id'] = user.user_id
        session['role'] = user.role

        log_user_login(user.user_id)

        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('employee_dashboard'))

    @app.route('/admin-login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            return redirect('/admin-dashboard')
        return render_template('admin_login.html')

    @app.route('/logout')
    def logout():
        user_id = session.get('user_id')

        if user_id:
            log_user_logout(user_id)
            session.clear()

        return redirect(url_for('login'))

    @app.route('/admin-dashboard')
    def admin_dashboard():
        employees = fetch_employees()  # Fetch dummy employees
        total_employees = len(employees)
        total_departments = fetch_departments_count()
        active_employees = fetch_active_employees_count()
        inactive_employees = total_employees - active_employees

        return render_template('admin_dashboard.html', employees=employees, total_employees=total_employees,
                               total_departments=total_departments, active_employees=active_employees,
                               inactive_employees=inactive_employees)
    


    # Route to insert data into database------------------------
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

        session.add(track_entry)
        session.commit()

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

