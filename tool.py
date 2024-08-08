import os
from app import db, Student, Class, Label, Teacher, TeacherInClass, StudentInClass, Account, Admin
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

def get_role():
    user_id = current_user.id
    admin = Admin.query.get(user_id)
    if admin:
        return 'admin'

    teacher = Student.query.get(user_id)
    if teacher:
        return 'teacher'

    student = Student.query.get(user_id)
    if student:
        return 'student'

    return 'unknown'