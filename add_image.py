import cv2
import face_recognition
import pandas as pd
from datetime import datetime
import os

# Function to load known faces
def load_known_faces(known_faces_dir):
    known_faces = []
    known_names = []
    for filename in os.listdir(known_faces_dir):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            image = face_recognition.load_image_file(os.path.join(known_faces_dir, filename))
            encoding = face_recognition.face_encodings(image)[0]
            known_faces.append(encoding)
            known_names.append(filename.split('.')[0])
    return known_faces, known_names

# Function to capture image
def capture_image():
    cam = cv2.VideoCapture(0)
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow('Press Space to capture', frame)
        key = cv2.waitKey(1)
        if key == ord(' '):
            return frame
        elif key == ord('q'):
            print("Exiting...")
            cam.release()
            cv2.destroyAllWindows()
            return None
    cam.release()
    cv2.destroyAllWindows()
    return None

# Function to save image
def save_image(image, name, save_dir='known_faces'):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    filename = os.path.join(save_dir, f"{name}.jpg")
    cv2.imwrite(filename, image)
    print(f"Image saved as {filename}")

# Function to recognize face
def recognize_face(captured_image, known_faces, known_names):
    face_encodings = face_recognition.face_encodings(captured_image)
    if len(face_encodings) == 0:
        print("No faces detected in the image.")
        return None
    captured_encoding = face_encodings[0]
    matches = face_recognition.compare_faces(known_faces, captured_encoding)
    if True in matches:
        first_match_index = matches.index(True)
        return known_names[first_match_index]
    return None

# Function to mark attendance and log events
def mark_attendance(student_name, file='attendance.xlsx', log_file='attendance_log.txt'):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    try:
        df = pd.read_excel(file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Name", "Date", "Time"])
    new_record_df = pd.DataFrame({"Name": [student_name], "Date": [current_date], "Time": [current_time]})
    df = pd.concat([df, new_record_df], ignore_index=True)
    df.to_excel(file, index=False)
    with open(log_file, 'a') as f:
        f.write(f"{current_date} {current_time} - {student_name}\n")

# Main execution
def main():
    known_faces_dir = 'known_faces'
    if os.listdir(known_faces_dir):  # Check if any images are available
        choice = input("Images already exist. Press 'c' to capture a new image, 'a' to take attendance, or 'q' to quit: ").lower()
        if choice == 'c':
            image = capture_image()
            if image is not None:
                name = input("Enter name for the new image: ")
                save_image(image, name)
        elif choice == 'a':
            known_faces, known_names = load_known_faces(known_faces_dir)
            print("Taking attendance...")
            image = capture_image()
            if image is not None:
                student_name = recognize_face(image, known_faces, known_names)
                if student_name is not None:
                    mark_attendance(student_name)
                    print(f"Attendance marked for {student_name}")
                else:
                    print("No recognized faces found in the captured image.")
        elif choice == 'q':
            return
        else:
            print("Invalid choice. Please try again.")
    else:
        print("No images found in the known faces directory. Please capture a new image.")
        while True:
            choice = input("Press 'c' to capture a new image or 'q' to quit: ").lower()
            if choice == 'c':
                image = capture_image()
                if image is not None:
                    name = input("Enter name for the new image: ")
                    save_image(image, name)
                    break
            elif choice == 'q':
                return
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
