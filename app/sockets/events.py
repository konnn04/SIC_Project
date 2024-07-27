from app import socketio
from flask import request
import base64
import io
from PIL import Image
import numpy as np
import imutils
import src.recognition as recognition
import time

last_processed_time = {}
COOLDOWN_PERIOD = 0.5

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('frame')
def handle_frame(data):
    sid = request.sid
    current_time = time.time()
    # Kiểm tra xem đã xử lý frame gần đây chưa (chống spam)
    if sid in last_processed_time and current_time - last_processed_time[sid] < COOLDOWN_PERIOD:
        return
    # Cập nhật thời gian xử lý frame gần đây
    last_processed_time[sid] = current_time
    print(f'Received frame from SID: {sid}')
    img_data = data['image']
    img_data = base64.b64decode(img_data)
    frame = Image.open(io.BytesIO(img_data)) 
    img_np = np.array(frame)
    frame = imutils.resize(img_np)
    results = recognition.frame_recognition(frame)    
    packet = {
        'persons_detected':[
        {
            'name': person['name'],
            'accuracy': person['accuracy'],
            'x1': person['x1'],
            'y1': person['y1'],
            'x2': person['x2'],
            'y2': person['y2'],
        }
        for person in results['persons_detected']
    ],
    }
    socketio.emit('update_results2', packet, room=sid)
   

# Thêm các SocketIO event handlers khác tại đây