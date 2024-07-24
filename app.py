from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import cv2
import os
import tensorflow.compat.v1 as tf
import random
import src.indentify as identify
import imutils
import time

FRAME = 15

# Load your model here
identify.start()

app = Flask(__name__)
socketio = SocketIO(app)

with app.app_context():  
    @app.route('/')
    def index():
        socketio.start_background_task(target=gen)
        return render_template("diemdanh.html")

    def gen():    
        cap = cv2.VideoCapture(0)              
        while True:
            
            success, frame = cap.read()
            if not success:
                break
            else:           
                frame = cv2.flip(frame, 1)               
                frame = imutils.resize(frame, width=600)

                best_name, best_class_probabilities, frame = identify.identify(frame)
                socketio.emit('update_results', {'name': best_name, 'accuracy': best_class_probabilities})
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            # time.sleep(round(1/FRAME, 2))
                    

    @app.route('/video_feed')
    def video_feed():    
        return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')

    @socketio.on('connect')
    def handle_connect():
        print("Client connected") 

    if __name__ == '__main__':
        # app.run(debug=True, threaded=True)
        socketio.run(app, debug=True)