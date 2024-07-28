from flask import Blueprint, render_template, redirect, url_for
from app import  socketio, Student, db, StudentCheckIn, Label
from app.sockets.events import handle_frame
from datetime import date

diemdanh_bp = Blueprint('diemdanh', __name__)

@diemdanh_bp.route('/diemdanh')
def diemdanh():
    today = date.today()
    db_all = db.session.query(Student.student_id, Student.svfname, Student.svlname, Student.class_id, StudentCheckIn.date,StudentCheckIn.time).\
        join(StudentCheckIn, Student.student_id == StudentCheckIn.student_id).all()
    socketio.start_background_task(target=handle_frame)
    return render_template('diemdanh.html', students_checkin=db_all)

@diemdanh_bp.route('/delete', methods=['POST'])
def delete():
    db.session.query(StudentCheckIn).delete()   
    db.session.commit()
    return redirect(url_for('diemdanh_diemdanh.diemdanh'))