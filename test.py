import cv2
import numpy as np
import face_recognition

def load_reference_image(image_path):
    reference_image = face_recognition.load_image_file(image_path)
    reference_encoding = face_recognition.face_encodings(reference_image)[0]
    return reference_encoding

def process_video_feed(reference_encoding):
    video_capture = cv2.VideoCapture(0)

    while True:
        ret, frame = video_capture.read()
        
        # Find all face locations and face encodings in the current frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare the face with the reference image
            matches = face_recognition.compare_faces([reference_encoding], face_encoding)
            
            if matches[0]:
                name = "Known Person"
                color = (0, 255, 0)  # Green
            else:
                name = "Unknown Person Detected"
                color = (0, 0, 255)  # Red

            # Draw a box around the face and label it
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

        # Display the resulting frame
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

# Usage
reference_image_path = "Profile.jpg"
reference_encoding = load_reference_image(reference_image_path)
process_video_feed(reference_encoding)