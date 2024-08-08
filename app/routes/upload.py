from flask import Blueprint, render_template, redirect, url_for,flash
from app import  socketio, Label
from app.sockets.events import handle_frame, handle_upload
from datetime import date
from flask_login import login_required, current_user
from tool import get_role

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload')
@login_required
def upload():
    if (get_role()!='student'):
        flash("Bạn không có quyền truy cập trang này!")
        return redirect(url_for("home_home.home"))
    socketio.start_background_task(target=handle_upload)

    label = Label.query.filter_by(idStudent=current_user.id).first()
    if (label is None):
        flash("Bạn chưa cập nhật sinh trắc học, vui lòng thực hiện!")
        return render_template('upload.html', status = 'none')
    if (label.status == 'pending'):
        flash("Sinh trắc học của bạn đang được xử lý, vui lòng chờ!")
        return render_template('upload.html', status = 'pending')
    if (label.status == 'done'):
        flash("Sinh trắc học của bạn đã được cập nhật!")
        return render_template('upload.html', status = 'done')

   