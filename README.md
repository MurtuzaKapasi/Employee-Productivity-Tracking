# Development of a System for Employee Productivity Monitoring and Analysis

# Employee Productivity Monitoring and Analysis  

This project is a **comprehensive system** designed to monitor employee activities and provide real-time insights into their productivity. It leverages advanced computer vision techniques, intuitive interfaces, and structured databases to ensure operational efficiency and transparency in workforce management.  

---

## Key Features  

### For Employees:  
- **Start Recording**: Begin and end work session tracking.  
- **Real-Time Activity Tracking**: Monitor work hours, meetings, breaks, and mobile usage.
- **Face Recognition**: Automated attendance verification using facial recognition.  

### For Admins:  
- **Employee Management**: View and manage employee details, activity logs, and productivity reports.  
- **Break and Meeting Tracking**: Access detailed logs of employee breaks, including durations and categories.  
- **Mobile Usage Monitoring**: Track mobile usage patterns to identify distractions.  
- **Data Insights**: Analyze team or department-level productivity trends through comprehensive metrics and reports.  

---

## Tech Stack  

### Backend  
- **Python (Flask)**: REST API development for real-time data handling.  
- **PostgreSQL**: Used for structured data storage.  
- **SQLAlchemy**: ORM for managing database operations.  

### Frontend  
- **HTML, CSS, JavaScript**: For the responsive and user-friendly interface.  
- **Bootstrap**: Ensures seamless UI/UX design.  

### Computer Vision and ML  
- **face_recognition**: Detects employee presence through webcam feeds.  
- **YOLO**: Identifies mobile usage and potential distractions.  

---

## Features Overview  

### **Employee Dashboard**  
1. **Login & Logout Tracking**:  
   - Start and stop work sessions.  
   - View real-time work session status.  

2. **Activity Logging**:  
   - Tracks meetings, breaks, and mobile usage.  
   - Logs lunch breaks with start and end times.  

3. **Personal Productivity Insights**:  
   - View daily and weekly productivity reports.  
   - Monitor overall performance with calculated productivity scores.  

### **Admin Dashboard**  
1. **Employee Management**:  
   - Add, update, or delete employee records.  
   - Monitor individual and team productivity levels.  

2. **Activity Analytics**:  
   - View detailed logs of breaks, meetings, and work hours.  
   - Identify bottlenecks and trends across departments.  

3. **Mobile Usage Monitoring**:  
   - Review mobile usage logs to identify distractions.  

4. **Performance Reports**:  
   - Generate custom reports for employee evaluations.  

---

## Table Design  

The system uses a normalized database with the following key tables:  

| **Table**           | **Description**                                                                 |
|----------------------|---------------------------------------------------------------------------------|
| `Employee`          | Stores employee details like name, role, department, and profile picture.       |
| `LoginLog`          | Logs login/logout timestamps and total working hours.                          |
| `RecordingLog`      | Logs activities like work hours, mobile usage, and productivity scores.        |  
| `BreakLog`          | Records break timings, durations, and categories.                              |
| `MeetingLog`        | Tracks meeting durations, participants, and details.                           |
| `MobileLog`         | Logs mobile usage time and type (e.g., calls, browsing).                       |  
| `LunchBreakLog`      | Tracks lunch break duration and status.                                        |  
| `EmployeeTracking`  | Tracks detailed activity metrics like breaks, meetings, and mobile usage.       |

---

## How It Works  

### 1. Data Capture  
- **Face Recognition**: Employees are identified via webcam.  
- **Object Detection**: Mobile usage is detected and logged.  
- **Manual Inputs**: Employees can start/stop work sessions and log meeting details.  

### 2. Data Processing  
- Real-time data is processed by the backend server and stored in the PostgreSQL database.  

### 3. Data Visualization  
- Admins and employees can view activity trends and productivity scores through intuitive dashboards.  

---
## Database Setup  

### Creating a Database User  
Run the following SQL commands to create a user and grant necessary permissions:  
```sql  
CREATE USER flask_user WITH PASSWORD 'Emp123';  
GRANT ALL PRIVILEGES ON DATABASE employee_tracking TO flask_user;  
GRANT ALL PRIVILEGES ON SCHEMA public TO flask_user;
```

Initializing the Database
Run the following Python commands in terminal to initialize the database tables:

```
from app import app, db  
with app.app_context():  
    db.create_all()  
```
---

## Deployment  

### Prerequisites  
1. Install Python 3.8+ and PostgreSQL.  

### Steps  
1. Clone the repository:  
   ```
   git clone https://github.com/your-username/employee-monitoring.git
   ```
2. Install dependencies:
```pip install -r requirements.txt  ```
3. Start the Flask server:
   ``` python app.py  ```
4. Access the platform at ```http://localhost:5000```.

---

## Results and Screenshots
### GUI and Features
* Login Page: Employee authentication via username/password.
* Dashboard: Displays productivity metrics and activity logs.
### Admin Reports
* Break and Meeting Logs: Admins can analyze trends and optimize schedules.
* Mobile Usage Insights: Detect distractions and suggest improvements.

---

## Future Scope
* AI-Based Predictions: Implement machine learning models to predict employee productivity.
* Mobile App Integration: Extend functionality to mobile platforms.
* nhanced Security: Add data encryption for privacy compliance.

## Contributors
- Murtuza Kapasi
- Sanket Kadam


