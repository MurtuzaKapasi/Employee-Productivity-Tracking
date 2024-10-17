# import cv2
# import time
# from datetime import datetime
# from ultralytics import YOLO  # Import YOLO model for object detection
# import requests  # Import requests to send data to Flask

# # Load the YOLOv10 model (for both face/person detection and phone detection)
# model = YOLO("../weights/yolov10n.pt")  # Adjust path to your YOLOv10 model
# # Start video capture from the laptop's camera
# cap = cv2.VideoCapture(0)

# # To store time logs of when the employee is not present and using the phone
# not_present_log = []
# phone_usage_log = []

# # Variables to track employee absence
# was_present = True
# absence_start_time = None
# total_absence_time = 0

# # Variables to track phone usage
# phone_usage_start_time = None
# total_phone_usage_time = 0

# # Record the start time
# start_time = time.time()
# duration = 60  # Capture duration in seconds (1 minute)

# while True:
#     # Capture frame-by-frame
#     ret, frame = cap.read()

#     # Check if frame was captured successfully
#     if not ret or frame is None:
#         print("Failed to grab frame, exiting...")
#         break

#     current_time = datetime.now()

#     # Perform object detection using YOLOv10
#     results = model.predict(source=frame, conf=0.25)

#     # Check for "person" class (class 0 in COCO) for face detection
#     persons_detected = []
#     phones_detected = []

#     for result in results:
#         for box in result.boxes:
#             cls = int(box.cls[0])  # Class of the detected object
#             conf = box.conf[0]     # Confidence of the detection
#             xyxy = box.xyxy[0]     # Bounding box coordinates

#             # Check if it's a person (class 0 in COCO)
#             if cls == 0:
#                 persons_detected.append((cls, conf, xyxy))
#             # Check if it's a phone (class 67 in COCO)
#             elif cls == 67:
#                 phones_detected.append((cls, conf, xyxy))

#             # Draw bounding boxes on the frame
#             x1, y1, x2, y2 = map(int, xyxy)
#             color = (0, 255, 0) if cls == 0 else (0, 0, 255)  # Green for person, red for phone
#             label = f"{model.names[cls]}: {conf:.2f}"

#             # Draw rectangle and label
#             cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#             cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

#     # If no person is detected, mark absence
#     if len(persons_detected) == 0:
#         if was_present:
#             # Log the time when the employee was detected to be away
#             absence_start_time = current_time
#             not_present_log.append(f"Absent started at {absence_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
#             was_present = False
#     else:
#         if not was_present and absence_start_time:
#             # Calculate the absence duration
#             absence_duration = (current_time - absence_start_time).total_seconds()
#             total_absence_time += absence_duration
#             absence_start_time = None
#             not_present_log.append(f"Absent ended at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
#         was_present = True

#     # If any phone is detected, log phone usage
#     if phones_detected:
#         if not phone_usage_start_time:
#             phone_usage_start_time = current_time
#             phone_usage_log.append(f"Phone usage started at {phone_usage_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
#     else:
#         if phone_usage_start_time:
#             # Calculate phone usage duration
#             phone_usage_duration = (current_time - phone_usage_start_time).total_seconds()
#             total_phone_usage_time += phone_usage_duration
#             phone_usage_start_time = None
#             phone_usage_log.append(f"Phone usage ended at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

#     # Display the resulting frame
#     cv2.imshow('Employee Tracking', frame)

#     # Break the loop if the duration exceeds
#     if time.time() - start_time > duration:
#         # If employee is still absent, calculate the ongoing absence time
#         if not was_present and absence_start_time:
#             absence_duration = (current_time - absence_start_time).total_seconds()
#             total_absence_time += absence_duration
#             not_present_log.append(f"Absent ended at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
#         break

#     # Break the loop on 'q' key press
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release the capture and close windows
# cap.release()
# cv2.destroyAllWindows()

# # Calculate total absence time in minutes and seconds
# total_absence_minutes, total_absence_seconds = divmod(total_absence_time, 60)

# # Calculate total phone usage time in minutes and seconds
# total_phone_usage_minutes, total_phone_usage_seconds = divmod(total_phone_usage_time, 60)

# # Print logs of the times the employee was not present and the total absence time
# print("Employee was not present at:")
# for log in not_present_log:
#     print(log)

# print(f"Total time absent: {int(total_absence_minutes)} minutes and {int(total_absence_seconds)} seconds")

# # Print logs of the times the employee was using the phone and the total phone usage time
# print("Employee was using phone at:")
# for log in phone_usage_log:
#     print(log)

# print(f"Total phone usage time: {int(total_phone_usage_minutes)} minutes and {int(total_phone_usage_seconds)} seconds")


# # Function to send logs to the Flask server
# def send_logs_to_server(total_absent_time, total_phone_usage_time):
#     url = 'http://127.0.0.1:5000/track'  # Your Flask server URL
#     payload = {
#         "employee_id": "12345",  # Track employee ID if needed
#         "total_absent_time": total_absent_time,
#         "total_phone_usage_time": total_phone_usage_time
#     }
#     try:
#         response = requests.post(url, json=payload)
#         print(f"Server Response: {response.status_code}, {response.json()}")
#     except Exception as e:
#         print(f"Failed to send data to server: {e}")

# # Send total absence and phone usage times to the Flask server
# send_logs_to_server(total_absence_time, total_phone_usage_time)








import cv2
import time
from datetime import datetime
import face_recognition
from ultralytics import YOLO
import numpy as np
import sys
from app import db, app  # Import db and app from your Flask app
from models import BreakLog, MobileLog, User, RecordingLog
import requests

# Load the YOLOv10 model (for phone detection)
model = YOLO("../weights/yolov10n.pt")  # Adjust path to your YOLOv10 model

# Start video capture
cap = cv2.VideoCapture(0)

# Get command line arguments for employee ID and email
if len(sys.argv) < 3:
    print("Not enough arguments provided.")
    sys.exit(1)

employee_id = sys.argv[1]
employee_email = sys.argv[2]

# Variables for tracking absence and breaks
absence_start_time = None
total_absence_time = 0
break_start_time = None

# Variables to track phone usage
phone_usage_start_time = None
total_phone_usage_time = 0

# Load the reference image of the employee (for face recognition)
with app.app_context():
    employee = User.query.filter_by(email=employee_email).first()
    
    if employee:
        employee_id = employee.id
        print(f"Employee found: {employee.user_name} with ID: {employee_id}")
        
        profile_picture = np.frombuffer(employee.profile_picture, np.uint8)
        reference_image = cv2.imdecode(profile_picture, cv2.IMREAD_COLOR)
        reference_encoding = face_recognition.face_encodings(reference_image)[0]
    else:
        print(f"No employee found with email {employee_email}")

# Track start recording details without committing immediately
start_recording_time = datetime.now()

last_check_time = time.time()

# Function to check user presence and log breaks
def check_presence(frame, current_time):
    global absence_start_time, break_start_time, total_absence_time

    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    user_found = False
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces([reference_encoding], face_encoding)
        if matches[0]:
            user_found = True
            if absence_start_time:
                absence_duration = (current_time - absence_start_time).total_seconds()
                if absence_duration > 15:
                    break_duration = absence_duration
                    break_end_time = current_time
                    with app.app_context():
                        new_break = BreakLog(
                            employee_id=employee_id,
                            start_time=absence_start_time,
                            end_time=break_end_time,
                            break_time=break_duration
                        )
                        db.session.add(new_break)
                        db.session.commit()
                    absence_start_time = None
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, "Present", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    if not user_found and absence_start_time is None:
        absence_start_time = current_time
        print(f"Employee {employee_id} absent at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

# Function to detect phone usage
def detect_phone(frame, current_time):
    global phone_usage_start_time, total_phone_usage_time
    results = model.predict(source=frame, conf=0.25)
    phones_detected = []

    for result in results:
        for box in result.boxes:
            cls = int(box.cls[0])
            conf = box.conf[0]
            xyxy = box.xyxy[0]
            if cls == 67:
                phones_detected.append((cls, conf, xyxy))
            x1, y1, x2, y2 = map(int, xyxy)
            if cls == 67:
                color = (0, 0, 255)
                label = f"Phone: {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    if phones_detected:
        if not phone_usage_start_time:
            phone_usage_start_time = current_time
            print(f"Phone usage started at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        if phone_usage_start_time:
            phone_usage_duration = (current_time - phone_usage_start_time).total_seconds()
            total_phone_usage_time += phone_usage_duration
            
            if phone_usage_duration > 5:
                print(f"Logging phone usage of {phone_usage_duration} seconds")
                phone_usage_end_time = current_time

                # Add to MobileLog table
                with app.app_context():
                    new_mobile_log = MobileLog(
                        employee_id=employee_id,
                        start_time=phone_usage_start_time,
                        end_time=phone_usage_end_time,
                        mobile_usage_time=phone_usage_duration
                    )
                    db.session.add(new_mobile_log)
                    db.session.commit()
                    print('Committed!')                    
            
            
            phone_usage_start_time = None
            print(f"Phone usage ended at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

while True:
    current_time = datetime.now()
    ret, frame = cap.read()
    if not ret or frame is None:
        print("Failed to grab frame, exiting...")
        break

    if time.time() - last_check_time >= 5:
        check_presence(frame, current_time)
        last_check_time = time.time()

    detect_phone(frame, current_time)
    cv2.imshow('Employee Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# # Send phone usage time to the stop-recording route
# try:
#     print('Sending phone usage time to the server...')  
#     response = requests.post(
#         "http://127.0.0.1:5000/stop-recording",  
#         json={'employee_id': employee_id, 'phone_usage_time': total_phone_usage_time}
#     )
#     print(f"Sent phone usage time: {total_phone_usage_time} seconds")  

#     # CHANGED: Debugging network issues with response status code
#     if response.status_code != 200:
#         print(f"Failed with status code: {response.status_code}, response: {response.text}")

# except requests.exceptions.RequestException as e:
#     print(f"Failed to send phone usage time: {e}")


# def get_phone_usage_time():
#     return total_phone_usage_time
