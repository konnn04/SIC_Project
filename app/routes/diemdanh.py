from flask import Blueprint, render_template, redirect, url_for, flash
from app import  socketio, Student, db, Attendance , Label
from app.sockets.events import handle_frame
from datetime import date
from flask_login import login_required, current_user
from tool import get_role

diemdanh_bp = Blueprint('diemdanh', __name__)

@diemdanh_bp.route('/diemdanh')

@login_required

def diemdanh():
    if (get_role()!= "teacher"):
        flash("Bạn không có quyền truy cập trang này!")
        return redirect(url_for("home_home.home"))
    
    today = date.today()
    db_all = db.session.query(Student.idStudent, Student.fname, Student.lname, Attendance.date,Attendance.time).\
        join(Attendance, Attendance.idStudent == Student.idStudent).all()
    socketio.start_background_task(target=handle_frame)
    return render_template('diemdanh.html', students_checkin=db_all)

@diemdanh_bp.route('/delete', methods=['POST'])
def delete():
    if (get_role()!= "teacher"):
        flash("Bạn không có quyền truy cập trang này!")
        return redirect(url_for("home_home.home"))
    
    db.session.query(Attendance).delete()   
    db.session.commit()
    socketio.emit('update_checkin_students', [])
    return redirect(url_for('diemdanh_diemdanh.diemdanh')) 