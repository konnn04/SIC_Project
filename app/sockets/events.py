from app import socketio
from flask import request
import base64
import io
from PIL import Image
import numpy as np
import imutils
import src.recognition as recognition
import time
from datetime import datetime
from app import Label, db, Student, StudentCheckIn

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
    update = False
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
    for result in results['persons_detected']:
        label_name = result['name']
        if (result['accuracy'] > 0.9):
            q_label = Label.query.filter_by(label_name=label_name).first()
            if (label_name != None) and (label_name != "") and q_label is not None:
                student_id = q_label.student_id
                date_time = datetime.now()
                if StudentCheckIn.query.filter_by(student_id=student_id, date=date_time.date()).first() is None:
                    student_check = StudentCheckIn(student_id=student_id,date = date_time.date(), time = date_time.time())
                    db.session.add(student_check)
                    db.session.commit()
                    update = True
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
        'update': update
    }
    socketio.emit('update_results2', packet, room=sid)

    if update:
        students = Student.query.join(StudentCheckIn).filter(StudentCheckIn.student_id == Student.student_id).with_entities(Student.student_id, Student.svfname, Student.svlname, Student.class_id, StudentCheckIn.date, StudentCheckIn.time).all()
        students = [
            {
                'student_id': student.student_id,
                'svfname': student.svfname,
                'svlname': student.svlname,
                'class_id': student.class_id,
                'date_time': student.date.strftime('%Y-%m-%d') + ' ' + student.time.strftime('%H:%M:%S')
            }
            for student in students
        ]
        students.sort(key=lambda x: x['date_time'], reverse=True)
        socketio.emit('update_checkin_students', students, room=sid)
   

# Thêm các SocketIO event handlers khác tại đây