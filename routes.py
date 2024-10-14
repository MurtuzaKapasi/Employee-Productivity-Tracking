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
        position = request.form.get('position')
        profile_picture = request.files['profile_picture']
        
        try:
            # Convert image to bytes
            image_bytes = profile_picture.read()
            
            # Create a new User object
            new_employee = User(
                user_name=name,
                email=email,
                password=password,  # Consider hashing this
                role=role,
                department=department,
                position=position,
                profile_picture=image_bytes  # Assuming you have a column for this
            )

            db.session.add(new_employee)
            db.session.commit()

            flash("Employee registered successfully!", 'success')
            return redirect(url_for('admin_dashboard'))

        except Exception as e:
            db.session.rollback()
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

        session['employee_id'] = user.id
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
        employee_id = session.get('employee_id')
        admin_id = session.get('admin_id')
        if employee_id:
            log_user_logout(employee_id)
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
        if 'employee_id' in session:
            return render_template('employee_dashboard.html')
        else:
            return render_template('not_logged.html')
   
# EMPLOYEE dashboard routes---------------------------------

    @app.route('/get-logs', methods=['GET'])
    def get_logs():
        # Query the employee tracking table for logs and stats
        employee_id = session.get('employee_id')  # Assuming the session has the employee id
        logs = EmployeeTracking.query.filter_by(employee_id=employee_id).all()

        total_absence_time = sum(log.idle_time_hours for log in logs if log.idle_time_hours is not None)
        total_phone_usage_time = sum(log.mobile_usage_minutes for log in logs)
        total_working_hours = sum(log.total_hours_worked for log in logs)

        # Format the logs into a dictionary
        log_data = [{'log_time': log.log_time, 'event': log.event} for log in logs]

        return jsonify({
            'total_absence_time': total_absence_time,
            'total_phone_usage_time': total_phone_usage_time,
            'total_working_hours': total_working_hours,
            'logs': log_data
        })

    @app.route('/submit-meeting', methods=['POST'])
    def submit_meeting():
        meeting_with = request.form['meeting_with']
        meeting_desc = request.form['meeting_desc']
        
        # Assuming you have the employee ID in session
        employee_id = session.get('employee_id')

        # Save meeting info to the employee tracking table
        new_meeting = EmployeeTracking(
            employee_id=employee_id,
            meeting_info=f"With: {meeting_with}, Desc: {meeting_desc}",
            meeting_hours=0  # Default meeting hours to 0, can be updated later
        )
        db.session.add(new_meeting)
        db.session.commit()

        return redirect(url_for('employee_dashboard'))
    
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
            # Save employee login time and start recording
            employee_id = session.get('employee_id')  
            login_time = datetime.now().strftime('%H:%M:%S')
            name = session.get('name')

            # Save login time in the EmployeeTracking table
            track_entry = EmployeeTracking(employee_id=employee_id, name=name, login_time=login_time)
            db.session.add(track_entry)
            db.session.commit()

            # Run the employee tracking script in the background
            subprocess.Popen(['python', 'employee_tracker.py'], shell=True)
            
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

    @app.route('/take-lunch', methods=['POST'])
    def take_lunch():
        try:
            employee_id = session.get('employee_id')
            confirmation = request.form.get('confirmation')  # Confirmation response from the popup

            if confirmation == 'pause':
                # Save the start of the lunch break in the database
                track_entry = EmployeeTracking.query.filter_by(employee_id=employee_id).order_by(EmployeeTracking.id.desc()).first()
                track_entry.lunch_start_time = datetime.now().strftime('%H:%M:%S')
                db.session.commit()

                return jsonify({'message': 'Lunch break started. Recording paused.'}), 200

            elif confirmation == 'resume':
                # Save the end of the lunch break and resume recording
                track_entry = EmployeeTracking.query.filter_by(employee_id=employee_id).order_by(EmployeeTracking.id.desc()).first()
                track_entry.lunch_end_time = datetime.now().strftime('%H:%M:%S')

                # Calculate total lunch duration
                lunch_duration = (datetime.strptime(track_entry.lunch_end_time, '%H:%M:%S') -
                                datetime.strptime(track_entry.lunch_start_time, '%H:%M:%S')).total_seconds() / 3600
                track_entry.lunch_duration = lunch_duration
                db.session.commit()

                return jsonify({'message': 'Lunch break finished. Recording resumed.'}), 200
            else:
                return jsonify({'error': 'Invalid confirmation response.'}), 400

        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    @app.route('/start-meeting', methods=['POST'])
    def start_meeting():
        try:
            employee_id = session.get('employee_id')
            meeting_info = request.form['meeting_info']  # Expecting whom and description
            track_entry = EmployeeTracking.query.filter_by(employee_id=employee_id).order_by(EmployeeTracking.id.desc()).first()

            # Save meeting start time and info in the database
            track_entry.meeting_start_time = datetime.now().strftime('%H:%M:%S')
            track_entry.meeting_info = meeting_info
            db.session.commit()

            # Optionally, pause the recording during the meeting
            track_entry.recording_paused = True
            db.session.commit()

            return jsonify({'message': 'Meeting started. Recording paused.'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/stop-meeting', methods=['POST'])
    def stop_meeting():
        try:
            employee_id = session.get('employee_id')
            track_entry = EmployeeTracking.query.filter_by(employee_id=employee_id).order_by(EmployeeTracking.id.desc()).first()

            # Save meeting end time
            track_entry.meeting_end_time = datetime.now().strftime('%H:%M:%S')

            # Calculate meeting duration
            meeting_duration = (datetime.strptime(track_entry.meeting_end_time, '%H:%M:%S') -
                                datetime.strptime(track_entry.meeting_start_time, '%H:%M:%S')).total_seconds() / 3600
            track_entry.meeting_duration = meeting_duration
            db.session.commit()

            # Resume recording after meeting ends
            track_entry.recording_paused = False
            db.session.commit()

            return jsonify({'message': 'Meeting ended. Recording resumed.'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/stop-recording', methods=['POST'])
    def stop_recording():
        try:
            # Get employee_id from session
            employee_id = session.get('employee_id')  # Ensure you set this when the user logs in
            if not employee_id:
                return jsonify({'message': 'User not logged in'}), 401

            # Get the current time as end_time
            end_time = datetime.now()

            # Fetch the employee record based on the employee_id
            employee_record = EmployeeTracking.query.filter_by(employee_id=employee_id).first()

            if not employee_record:
                return jsonify({'message': 'Employee not found'}), 404
            
            # Stop recording: update end_time and calculate total working hours
            employee_record.end_time = end_time
            total_working_hours = (end_time - employee_record.start_time).total_seconds() / 3600.0
            employee_record.total_working_hours = total_working_hours
            db.session.commit()  # Save changes to the database

            return jsonify({'message': 'Recording stopped successfully', 'total_working_hours': total_working_hours}), 200

        except Exception as e:
            return jsonify({'message': str(e)}), 500  # Internal Server Error
