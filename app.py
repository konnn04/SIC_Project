import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ['TF_ENABLE_ONEDNN_OPTS'] = "0"
import src.recognition as rec

from app import app, socketio, db, Student, Class, Label, Teacher, TeacherInClass, Admin, StudentInClass,  StudentInClass, Account
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import redirect, url_for
from datetime import timedelta

def init_db():
    db.create_all()
    print("Các bảng cơ sở dữ liệu đã được tạo.")
    # Kiểm tra xem tài khoản admin đã

    admin = Admin.query.filter_by(idAdmin='admin').first()
    if not admin:
            # Tạo tài khoản admin mặc định
            admin_account = Admin(idAdmin='admin', fname='admin', lname='', sex="none", address='none')
            db.session.add(admin_account)
            db.session.commit()
            print("Tài khoản admin mặc định đã được tạo.")
    admin_account = Account.query.filter_by(id='admin').first()
    if not admin_account:
        # Tạo tài khoản admin mặc định
        admin_account = Account(id='admin', password='admin')
        db.session.add(admin_account)
        db.session.commit()
        print("Tài khoản admin_accout mặc định đã được tạo.")

if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        init_db()
    rec.init()
    socketio.run(app, debug=True)