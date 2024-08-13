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
from flask_login import current_user
from src.processing import augment_image

last_processed_time = {}
save_temp = {}
COOLDOWN_PERIOD = 1
COOLDOWN_PERIOD_UPLOAD = .2

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
            q_label = Label.query.filter_by(dataName=label, status='done').first()
            if q_label is not None:
                student_id = q_label.idStudent
                date_time = datetime.now()
                if Attendance.query.filter_by(idStudent=student_id, date=date_time.date()).first() is None:
                    student_check = Attendance(idStudent=student_id,date = date_time.date(), time = date_time.time())
                    db.session.add(student_check)
                    update = True
    persons_detected = []
    
    persons = results['persons_detected']

    for person in persons:        
        q = Label.query.filter_by(dataName=person['name'], status='done').first()
        if q is not None:
            s= Student.query.get(q.idStudent)
            persons_detected.append({
                'accuracy': person['accuracy'],
                'x1': person['x1'],
                'y1': person['y1'],
                'x2': person['x2'],
                'y2': person['y2'],
                'name': s.lname + " " + s.fname
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
                'student_id': student.idStudent,
                'fname': student.fname,
                'lname': student.lname,
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
    imgs,type_img = augment_image(frame)

    if sid in save_temp and save_temp[sid]['len'] is not None:
        n = save_temp[sid]['len']
        err = False
        results = []
        i=0
        for i,img in enumerate(imgs):
            # frame = np.array(img)
            results.append(recognition.face_detection(img, recognition.pnet, recognition.rnet, recognition.onet))
            if 'error' in results[i] or err:
                err = True
                break   
            Image.fromarray(results[i]['face']).save(os.path.join(save_temp[sid]['path'], f'{n}_{type_img[i]}.jpg'))
        if (err):
            socketio.emit('update_result', {'status': 'error', 'message': results[i]['error']})
            return
        save_temp[sid]['len']+=1
        n = save_temp[sid]['len']
        socketio.emit('update_result', {'status': 'success', 'message': 'Upload success', 'bb': results[0]['bb'],'progress':save_temp[sid]['len'] / 100})
        if n>=100:
            if n>100:
                return
            else:
                l = Label.query.get(current_user.id)
                if (l is not None):
                    Label.query.filter_by(idStudent=current_user.id).delete()
                label = Label(idStudent=current_user.id, dataName = f'{current_user.id}_{sid}', status = 'pending')
                db.session.add(label)
                db.session.commit()
                save_temp[sid] = {}
                return 
    else:
        save_temp[sid] = {
            'path':os.path.join('dataset/temp', f'{current_user.id}_{sid}'),
            'len':0
        }
        os.mkdir(save_temp[sid]['path'])

         
        
    
   
    
    
    
    
    