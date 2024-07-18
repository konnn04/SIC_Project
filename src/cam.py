import cv2
import os

# Create the output directory if it doesn't exist
output_dir = 'dataset/output'
os.makedirs(output_dir, exist_ok=True)

# Load the pre-trained Haar cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize the webcam
cap = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Crop and save the detected faces
    for (x, y, w, h) in faces:
        face = frame[y:y+h, x:x+w]
        cv2.imwrite(os.path.join(output_dir, f'face_{len(os.listdir(output_dir))}.jpg'), face)

    # Display the frame with bounding boxes around the detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Display the resulting frame
    try:
        cv2.imshow('Face Detection', frame)
    except:
        print('Error')

    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()