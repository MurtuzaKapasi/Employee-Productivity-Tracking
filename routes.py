import base64
import platform
import subprocess
import traceback
from flask import flash, request, render_template, session, redirect, url_for, jsonify
import psutil
from utilities import fetch_active_employees_count, fetch_departments_count, fetch_employees, log_start_recording, log_stop_recording, verify_password, fetch_user_by_email, hash_password, log_user_login, log_user_logout,register_employee
from models import EmployeeTracking, User,db, LoginLog, MeetingLog, BreakLog, LunchBreakLog, RecordingLog
from datetime import date, datetime
import os
import signal



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

        # Initialize a variable to hold image bytes
        image_bytes = None

        # Check if the image was captured from the webcam
        if 'profile_picture' in request.form and request.form['profile_picture']:
            image_data = request.form['profile_picture']
            header, encoded = image_data.split(',', 1)  # Split header from data
            image_bytes = base64.b64decode(encoded)  # Decode base64 data

        # Check if an image file was uploaded
        elif 'profile_picture_upload' in request.files and request.files['profile_picture_upload'].filename != '':
            profile_picture_upload = request.files['profile_picture_upload']
            image_bytes = profile_picture_upload.read()  # Read uploaded file bytes

        # If no image is provided, return an error
        if image_bytes is None:
            flash("No profile picture provided. Please capture or upload an image.", 'danger')
            return redirect(url_for('register_employee'))

        try:
            # Create a new User object (assuming you have a User model)
            new_employee = User(
                user_name=name,
                email=email,
                password=password,  # Consider hashing this
                role=role,
                department=department,
                position=position,
                profile_picture=image_bytes  # Store the captured or uploaded image
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
            # Get employee details from session
            employee_id = session.get('employee_id')  
            employee_email = session.get('email')

            if not employee_id or not employee_email:
                return jsonify({'error': 'Employee ID or email not found in session.'}), 400

            # Log start recording time
            log_start_recording(employee_id)

            # Run the employee tracking script in the background
            process = subprocess.Popen(['python', 'employee_tracker.py', str(employee_id), employee_email], shell=True)
            session['tracker_pid'] = process.pid  # Save the process ID in session

            return jsonify({'message': 'Recording started successfully!'}), 200

        except Exception as e:
            # Print error to console for debugging
            print(f"Error occurred: {str(e)}")
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

    @app.route('/start-lunch', methods=['POST'])
    def start_lunch():
        try:
            employee_id = session.get('employee_id')

            # Get today's date
            today_date = date.today()

            # Check if a lunch break already exists for today for the employee
            existing_lunch = LunchBreakLog.query.filter_by(employee_id=employee_id).filter(
                db.func.date(LunchBreakLog.start_time) == today_date).first()

            if existing_lunch:
                return jsonify({'error': 'Lunch break already started today.'}), 400

            # Start the lunch break and log the start_time in LunchBreakLog
            new_lunch_break = LunchBreakLog(
                employee_id=employee_id,
                start_time=datetime.now(),
                is_active=True  # Mark the lunch break as active
            )
            db.session.add(new_lunch_break)
            db.session.commit()

            return jsonify({'message': 'Lunch break started.'}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    @app.route('/end-lunch', methods=['POST'])
    def end_lunch():
        try:
            employee_id = session.get('employee_id')

            # Fetch the active lunch break entry
            lunch_break = LunchBreakLog.query.filter_by(employee_id=employee_id, is_active=True).first()

            if not lunch_break:
                return jsonify({'error': 'No active lunch break found.'}), 400

            # Update the lunch break entry with end time and duration
            lunch_break.end_time = datetime.now()
            lunch_break.lunch_duration = (lunch_break.end_time - lunch_break.start_time).total_seconds() / 60.0
            lunch_break.is_active = False
            db.session.commit()

            return jsonify({'message': 'Lunch break ended.', 'duration': lunch_break.lunch_duration}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    @app.route('/start-meeting', methods=['POST'])
    def start_meeting():
        try:
            employee_id = session.get('employee_id')
            meeting_with = request.form['meeting_with']
            meeting_desc = request.form['meeting_desc']

            # Check if recording is active
            recording_active = session.get('recording_log_id')  # Assuming you store this flag in session

            if recording_active:
                return jsonify({'message': 'Recording is currently active. Please stop the recording before starting a meeting.'}), 200

            meeting_log = MeetingLog.query.filter_by(employee_id=employee_id).order_by(MeetingLog.id.desc()).first()
            if meeting_log and meeting_log.is_active:
                return jsonify({'message': 'Meeting is currently active. Please stop the meeting before starting a new one.'}), 200
            
            # Create a new MeetingLog entry
            new_meeting_log = MeetingLog(
                employee_id=employee_id,
                meeting_start_time=datetime.now(),
                meeting_with=meeting_with,
                meeting_desc=meeting_desc,
                per_meeting_hours=0,
                is_active=True
            )

            db.session.add(new_meeting_log)
            db.session.commit()

            # Store meeting ID in session for later use
            session['meeting_id'] = new_meeting_log.id

            print(f"Meeting ID: {new_meeting_log.id}")
            print("Successfully started meeting.")
            return jsonify({'message': 'Meeting started successfully.', 'meeting_id': new_meeting_log.id}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    @app.route('/stop-meeting', methods=['POST'])
    def stop_meeting():
        try:
            meeting_id = session.get('meeting_id')
            
            if not meeting_id:
                return jsonify({'error': 'No active meeting found.'}), 400

            # Fetch the meeting log entry
            meeting_log = MeetingLog.query.get(meeting_id)
            
            if not meeting_log or not meeting_log.is_active:
                return jsonify({'error': 'Meeting not found or already ended.'}), 400

            # Update the meeting log with end time and duration
            meeting_log.meeting_end_time = datetime.now()
            duration_seconds = (meeting_log.meeting_end_time - meeting_log.meeting_start_time).total_seconds()
            meeting_log.per_meeting_hours = duration_seconds / 3600.0
            meeting_log.is_active = False
            
            db.session.commit()
            
            # Clear the meeting ID from session
            session.pop('meeting_id', None)

            return jsonify({'message': 'Meeting stopped successfully!', 'duration': meeting_log.per_meeting_hours}), 200

        except Exception as e:
            print(f"Error occurred in stop-meeting: {str(e)}")
            return jsonify({'error': str(e)}), 500
        
    @app.route('/stop-recording', methods=['POST'])
    def stop_recording():
        try:
            # Get the process ID from session
            tracker_pid = session.get('tracker_pid')
            
            if not tracker_pid:
                return jsonify({'error': 'No recording process found.'}), 400

            # Terminate the process and all its children
            if platform.system() == 'Windows' or platform.system() == 'Linux' or platform.system() == 'Darwin':
                try:
                    print('Terminating process:', tracker_pid)
                    # Get the parent process
                    parent_process = psutil.Process(tracker_pid)
                    
                    # Terminate all child processes
                    children = parent_process.children(recursive=True)
                    for child in children:
                        child.terminate()  # or child.kill() for force kill
                    parent_process.terminate()  # or parent_process.kill() for force kill
                    
                    # Wait for processes to terminate
                    for child in children:
                        child.wait()
                    parent_process.wait()
                    
                except psutil.NoSuchProcess:
                    return jsonify({'error': 'Process not found.'}), 400

            # Clear the tracker_pid from session
            session.pop('tracker_pid', None)

            # Log the stop of recording and update the tracking data
            employee_id = session.get('employee_id')
            if employee_id:
                log_stop_recording()
                return jsonify({'message': 'Recording stopped successfully!'}), 200
            else:
                return jsonify({'error': 'Employee not found in session'}), 400

        except Exception as e:
            print(f"Error occurred in stop-recording: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
