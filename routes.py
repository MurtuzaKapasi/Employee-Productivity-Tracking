import subprocess
from flask import flash, request, render_template, session, redirect, url_for, jsonify
from utilities import fetch_active_employees_count, fetch_departments_count, fetch_employees, verify_password, fetch_user_by_email, hash_password, log_user_login, log_user_logout,register_employee
from models import EmployeeTracking, User,db, LoginLog
from datetime import datetime


def init_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/register-employee', methods=['GET'])
    def register_employee_page():
        return render_template('register_employee.html')

    @app.route('/register-employee', methods=['POST'])
    def register_employee_handle():
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        department = request.form.get('department')

        # hashed_password = generate_password_hash(password)

        try:
        # Create a new User object and add it to the database
            new_employee = User(user_name=name, email=email, password=password, role=role, department=department)
            db.session.add(new_employee)
            db.session.commit()

            flash("Employee registered successfully!", 'success')
            return redirect(url_for('admin_dashboard'))

        except Exception as e:
            db.session.rollback()  # Roll back any changes if something goes wrong
            flash(f"Error: {str(e)}", 'danger')
            return render_template('register_employee.html'), 400
        
    @app.route('/login')
    def login():
        return render_template('login.html')

    @app.route('/manual-login', methods=['GET'])
    def manual_login_page():
        return render_template('manual_login.html')
    
    @app.route('/manual-login', methods=[ 'POST'])
    def manual_login():
        email = request.form['email']
        password = request.form['password']

        user = fetch_user_by_email(email)
        if not user or not verify_password(user.password, password):
            return "Invalid credentials!", 401

        session['user_id'] = user.id
        session['role'] = user.role
        session['name'] = user.user_name
        session['email'] = user.email

        log_user_login(user.id)

        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('employee_dashboard'))

    @app.route('/admin-login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            # Query the User model to find the admin user
            admin = User.query.filter_by(email=username, role='admin').first()
            
            # Check if admin exists and the password matches
            if admin and verify_password(admin.password, password):
                # Set a session variable to indicate the user is logged in
                session['admin_logged_in'] = True
                session['admin_id'] = admin.id  # Save admin id in session for later use
                session['name'] = admin.user_name  

                flash('Login successful', 'success')
                return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard
            else:
                # In case of invalid login, don't re-render the page, just pass 'invalid' in query params
                flash('Invalid credentials', 'danger')
                return redirect(url_for('admin_login', alert='invalid'))
        else:
            return render_template('admin_login.html')

    @app.route('/logout')
    def logout():
        user_id = session.get('user_id')
        admin_id = session.get('admin_id')
        if user_id:
            log_user_logout(user_id)
            session.clear()
        elif admin_id:
            log_user_logout(admin_id)
            session.clear()

        return redirect(url_for('index'))

    @app.route('/admin-dashboard')
    def admin_dashboard():
        employees = fetch_employees() 
        total_employees = len(employees)
        total_departments = fetch_departments_count()
        active_employees = fetch_active_employees_count()
        inactive_employees = total_employees - active_employees
        if 'admin_id' in session:
            return render_template('admin_dashboard.html', employees=employees, total_employees=total_employees,
                               total_departments=total_departments, active_employees=active_employees,
                               inactive_employees=inactive_employees)
        else:
            return render_template('not_logged.html')
    
    @app.route('/employee-dashboard')
    def employee_dashboard():
        if 'user_id' in session:
            return render_template('employee_dashboard.html')
        else:
            return render_template('not_logged.html')
   
   
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

