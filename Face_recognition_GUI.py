import cv2
import face_recognition
import tkinter as tk
from tkinter import messagebox
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
            break
        elif key == ord('q'):
            print("Exiting...")
            cam.release()
            cv2.destroyAllWindows()
            return None
    cam.release()
    cv2.destroyAllWindows()
    return frame

# Function to save image
def save_image(image, name, save_dir='known_faces'):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    filename = os.path.join(save_dir, f"{name}.jpg")
    cv2.imwrite(filename, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
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
def mark_attendance(student_name):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")
    attendance_log = f"{current_date} {current_time} - {student_name}"
    print(attendance_log)
    with open('attendance_log.txt', 'a') as f:
        f.write(attendance_log + '\n')

# Main execution
class FaceRecognitionApp:
    def __init__(self, master):
        self.master = master
        master.title("Face Recognition")

        self.label = tk.Label(master, text="Face Recognition Program")
        self.label.pack()

        self.add_button = tk.Button(master, text="Add New Image", command=self.add_new_image)
        self.add_button.pack()

        self.attendance_button = tk.Button(master, text="Take Attendance", command=self.take_attendance)
        self.attendance_button.pack()

        self.quit_button = tk.Button(master, text="Quit", command=master.quit)
        self.quit_button.pack()

    def add_new_image(self):
        new_image_window = tk.Toplevel(self.master)
        new_image_window.title("Add New Image")

        # Capture image when adding a new image
        image = capture_image()
        if image is not None:
            name_label = tk.Label(new_image_window, text="Enter name for the new image:")
            name_label.pack()

            name_entry = tk.Entry(new_image_window)
            name_entry.pack()

            save_button = tk.Button(new_image_window, text="Save Image", command=lambda: self.save_new_image(image, name_entry.get()))
            save_button.pack()

    def save_new_image(self, image, name):
        save_image(image, name)
        messagebox.showinfo("Image Saved", f"Image saved as {name}.jpg")

    def take_attendance(self):
        known_faces_dir = 'known_faces'
        known_faces, known_names = load_known_faces(known_faces_dir)

        # Continuous image capture for attendance
        while True:
            image = capture_image()
            if image is None:
                break
            student_name = recognize_face(image, known_faces, known_names)
            if student_name is not None:
                mark_attendance(student_name)
                # Display recognized student name on the image window
                cv2.putText(image, f"Recognized: {student_name}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.imshow('Recognized Image', image)
                cv2.waitKey(2000)  # Display recognized image for 3 seconds
                cv2.destroyAllWindows()
                # messagebox.showinfo("Attendance Marked", f"Attendance marked for {student_name}")
                # Break the loop after marking attendance for one student
            else:
                messagebox.showinfo("Unknown Face", "No recognized faces found in the captured image.")

def main():
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
