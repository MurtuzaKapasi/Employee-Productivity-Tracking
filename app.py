from flask import Flask, request, jsonify
from config import Config
from models import db, EmployeeTracking
from datetime import datetime
import subprocess  # Import subprocess to run the employee_tracking.py

app = Flask(__name__)
app.config.from_object(Config)

# Initialize the database with Flask
db.init_app(app)

# Root route
@app.route('/')
def home():
    return "Welcome to the Employee Tracking System!"

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
        # Run the employee_tracking.py file
        subprocess.Popen(['python', 'employee_tracker.py'])  # Adjust the path to your file
        return jsonify({'message': 'Recording started successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
