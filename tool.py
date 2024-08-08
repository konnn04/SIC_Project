import os
from app import db, Student, Class, Label, Teacher, TeacherInClass, TeacherAccount, StudentInClass, StudentAccount, StudentInClass, AdminAccount
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

def get_role():
    user_id = current_user.id
    admin_account = AdminAccount.query.get(user_id)
    if admin_account:
        return 'admin'

    teacher_account = TeacherAccount.query.get(user_id)
    if teacher_account:
        return 'teacher'

    student_account = StudentAccount.query.get(user_id)
    if student_account:
        return 'student'

    return 'unknown'