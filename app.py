import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ['TF_ENABLE_ONEDNN_OPTS'] = "0"
import src.recognition as rec

from app import app, socketio, db, Student, Class, Label, Teacher, TeacherInClass, TeacherAccount, StudentInClass, StudentAccount, StudentInClass, AdminAccount
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import redirect, url_for
from datetime import timedelta

def init_db():
    db.create_all()
    print("Các bảng cơ sở dữ liệu đã được tạo.")
    
    teacher_account = TeacherAccount.query.filter_by(id='2201').first()
    if not teacher_account:
        teacher_account = TeacherAccount(id='2201', password='1234')
        db.session.add(teacher_account)
        db.session.commit()
        print("Tài khoản giáo viên mặc định đã được tạo.")

    student_account = StudentAccount.query.filter_by(id='2251052127').first()
    if not student_account:
        student_account = StudentAccount(id='2251052127', password='1234')
        db.session.add(student_account)
        db.session.commit()
        print("Tài khoản sinh viên mặc định đã được tạo.")

    admin_account = AdminAccount.query.filter_by(id='admin').first()
    if not admin_account:
        # Tạo tài khoản admin mặc định
        admin_account = AdminAccount(id='admin', password='admin')
        db.session.add(admin_account)
        db.session.commit()
        print("Tài khoản admin mặc định đã được tạo.")

    student = Student.query.filter_by(idStudent = '2251052127').first()
    # if not student:
    #     # Tạo sinh viên mẫu
    #     # student = Student(idStudent = '2251052127', fname = 'Nguyễn', lname = 'Văn A', 


if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        init_db()
    rec.init()
    socketio.run(app, debug=True)