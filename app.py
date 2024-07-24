from flask import Flask, render_template, Response, request, jsonify
import cv2
import os
# import face_recognition
import numpy as np

app = Flask(__name__)

# Load your model here
# model = load_model()

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template("diemdanh.html")

def gen():
    """Video streaming generator function."""
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Convert the image from BGR color (which OpenCV uses) to RGB color
            rgb_frame = frame[:, :, ::-1]

            # Now you can use face_recognition library to recognize faces
            # For example, if you have a loaded model to predict
            # face_locations = face_recognition.face_locations(rgb_frame)
            # face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            # predictions = model.predict(face_encodings)

            # Just for demonstration, we will convert the frame to JPEG and return it
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/submit', methods=['POST'])
def submit():
    # Here you would process the image sent from the form to recognize the face
    # For simplicity, we'll just return a dummy response
    data = request.json
    # Process data['image'] with your face recognition model
    # For now, we'll just pretend we recognized a face with 99% accuracy
    response = {'label': 'John Doe', 'accuracy': 99}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, threaded=True)