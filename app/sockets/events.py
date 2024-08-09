from app import socketio
from flask import request
import os
import base64
import io
from PIL import Image
import numpy as np
import imutils
import src.recognition as recognition
import time
from datetime import datetime
from app import  db, Attendance, Student, Label
from sqlalchemy.orm import joinedload

last_processed_time = {}
save_temp = {}
COOLDOWN_PERIOD = 1
COOLDOWN_PERIOD_UPLOAD = .5

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
    # print(f'Received frame from SID: {sid}')
    img_data = data['image']
    img_data = base64.b64decode(img_data)
    frame = Image.open(io.BytesIO(img_data)) 
    img_np = np.array(frame)
    frame = imutils.resize(img_np)
    results = recognition.frame_recognition(frame)    
    for result in results['persons_detected']:
        label = result['name']
        if (result['accuracy'] > 0.9):
            q_label = Label.query.filter_by(idStudent=label).first()
            if q_label is not None:
                student_id = q_label.idStudent
                date_time = datetime.now()
                if Attendance.query.filter_by(idStudent=student_id, date=date_time.date()).first() is None:
                    student_check = Attendance(idStudent=student_id,date = date_time.date(), time = date_time.time())
                    db.session.add(student_check)
                    update = True
    persons_detected = []
    
    person_names = [person['name'] for person in results['persons_detected']]

    students =  Student.query.join(Label).filter(Label.idStudent.in_(person_names)).options(joinedload(Student.labels)).all()

    student_dict = {label.lidStudent: student for student in students for label in student.labels}

    for person in results['persons_detected']:        
        q = student_dict.get(person['name'])
        persons_detected.append({
            'accuracy': person['accuracy'],
            'x1': person['x1'],
            'y1': person['y1'],
            'x2': person['x2'],
            'y2': person['y2'],
            'name': q.lname +" "+q.fname if q is not None else 'Unknown'
        })
    packet = {
        'persons_detected': persons_detected,
        'update': update
    }
    socketio.emit('update_results2', packet, room=sid)

    if update:
        db.session.commit()
        students = Student.query.join(Attendance).filter(Attendance.idStudent == Student.idStudent).with_entities(Student.idStudent, Student.fname, Student.lname, Attendance.date, Attendance.time).all()
        students = [
            {
                'student_id': student.student_id,
                'fname': student.svfname,
                'lname': student.svlname,
                # 'class_id': student.class_id,
                'date_time': student.date.strftime('%Y-%m-%d') + ' ' + student.time.strftime('%H:%M:%S')
            }
            for student in students
        ]
        students.sort(key=lambda x: x['date_time'], reverse=True)
        socketio.emit('update_checkin_students', students)
   
@socketio.on('upload')
def handle_upload(data):
    update = False
    sid = request.sid
    current_time = time.time()
    if sid in last_processed_time and current_time - last_processed_time[sid] < COOLDOWN_PERIOD_UPLOAD:
        return        
    last_processed_time[sid] = current_time

    img_data = data['image']
    img_data = base64.b64decode(img_data)
    frame = Image.open(io.BytesIO(img_data)) 
    frame = np.array(frame)
    results = recognition.face_detection(frame, recognition.pnet, recognition.rnet, recognition.onet)

    if 'error' in results:
        socketio.emit('update_result', {'status': 'error', 'message': results['error']})
        return

    if sid in save_temp:
        n = save_temp[sid]['len']
        Image.fromarray(results['face']).save(os.path.join(save_temp[sid]['path'], f'{n}.jpg'))
        save_temp[sid]['len']+=1
        if n>=100:
            return 
        socketio.emit('update_result', {'status': 'success', 'message': 'Upload success', 'bb': results['bb'],'progress':save_temp[sid]['len'] / 100})
    else:
        save_temp[sid] = {
            'path':os.path.join('dataset/temp', f'temp_{sid}'),
            'len':0
        }
        os.mkdir(save_temp[sid]['path'])
    
   
    
    
    
    
    