from flask import Blueprint, render_template
from app import db, socketio, Student
from app.sockets.events import handle_frame

diemdanh_bp = Blueprint('diemdanh', __name__)

@diemdanh_bp.route('/diemdanh')
def diemdanh():
    db_all = Student.query.all()  # Lấy tất cả sinh viên để hiển thị
    socketio.start_background_task(target=handle_frame)
    return render_template('diemdanh.html', students=db_all)