
import os
from flask import Flask, Blueprint, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask_socketio import SocketIO
import importlib
from flask_migrate import Migrate


# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Khởi tạo SocketIO
socketio = SocketIO(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_login.login'

#bao mat
app.config["SECRET_KEY"] = "tri"
app.permanent_session_lifetime = timedelta(minutes=1)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Class(db.Model):
    __tablename__ = 'class_'
    idClass = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    # relationship
    teachers_class = db.relationship('TeacherInClass', back_populates='class_', cascade='all, delete-orphan')
    students_class = db.relationship('StudentInClass', back_populates='class_', cascade='all, delete-orphan')
    
class TeacherInClass(db.Model):
    __tablename__ = 'teacher_in_class'
    idClass = db.Column(db.String, db.ForeignKey('class_.idClass'), nullable=False, primary_key=True)
    idTeacher = db.Column(db.String, db.ForeignKey('teacher.idTeacher'), nullable=False, primary_key=True)
    
    class_ = db.relationship('Class', back_populates='teachers_class')
    teacher = db.relationship('Teacher', back_populates='classes')

class Teacher(db.Model):
    __tablename__ = 'teacher'
    idTeacher = db.Column(db.String, primary_key=True)
    fname = db.Column(db.String, nullable=False)
    lname = db.Column(db.String, nullable=False)
    sex = db.Column(db.String, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    address = db.Column(db.String, nullable=False)

    teacher_accounts = db.relationship('TeacherAccount', back_populates='teacher')
    classes = db.relationship('TeacherInClass', back_populates='teacher', cascade='all, delete-orphan')
    
class TeacherAccount(db.Model, UserMixin):
    __tablename__ = 'teacheraccount'
    id = db.Column(db.String, db.ForeignKey('teacher.idTeacher'), primary_key=True, nullable=False)
    password = db.Column(db.String, nullable=False)    

    teacher = db.relationship('Teacher', back_populates='teacher_accounts')

    def check_password(self, password):
        return self.password == password

class StudentInClass(db.Model):
    __tablename__ = 'student_in_class'
    idClass = db.Column(db.String, db.ForeignKey('class_.idClass'), nullable=False, primary_key=True)
    idStudent = db.Column(db.String, db.ForeignKey('student.idStudent'), nullable=False, primary_key=True)

    class_ = db.relationship('Class', back_populates='students_class')
    student = db.relationship('Student', back_populates='classes')



class Student(db.Model):
    __tablename__ = 'student'
    idStudent = db.Column(db.String, primary_key=True)
    fname = db.Column(db.String, nullable=False)
    lname = db.Column(db.String, nullable=False)
    sex = db.Column(db.String, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    address = db.Column(db.String, nullable=False)
    
    student_accounts = db.relationship('StudentAccount', back_populates='student', cascade='all, delete-orphan')
    classes = db.relationship('StudentInClass', back_populates='student', cascade='all, delete-orphan')
    labels = db.relationship('Label', back_populates='student', cascade='all, delete-orphan')
    attendances = db.relationship('Attendance', back_populates='student', cascade='all, delete-orphan')

class StudentAccount(db.Model, UserMixin):
    __tablename__ = 'studentaccount'
    id = db.Column(db.String, db.ForeignKey("student.idStudent"), primary_key=True, nullable=False)
    password = db.Column(db.String, nullable=False)    

    student = db.relationship('Student', back_populates='student_accounts')

    def check_password(self, password):
        return self.password == password

class Label(db.Model):
    __tablename__ = 'label'
    idStudent = db.Column(db.String, db.ForeignKey('student.idStudent'), primary_key=True)
    dataName = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)

    student = db.relationship('Student', back_populates='labels')

class Attendance(db.Model):
    __tablename__ = 'attendance'
    idStudent = db.Column(db.String, db.ForeignKey('student.idStudent'), primary_key=True)
    date = db.Column(db.Date, primary_key=True)
    time = db.Column(db.Time, nullable=False)
    # 
    student = db.relationship('Student', back_populates='attendances')

class AdminAccount(db.Model, UserMixin):
    __tablename__ = 'adminaccount'
    id = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=False)

    def check_password(self, password):
        return self.password == password

# def init_db():
#     with app.app_context():
#         db.create_all()        
#         print("Các bảng cơ sở dữ liệu đã được tạo.")

# Import routes và socket events
from app.sockets import events

# Import các Blueprint từ các file routes
def register_blueprints(app):
    # Lấy đường dẫn tới thư mục chứa các file routes
    routes_dir = os.path.join(os.path.dirname(__file__), 'routes')
    for filename in os.listdir(routes_dir):
        # Nếu là file python và không phải là file __init__.py
        if filename.endswith('.py') and filename != '__init__.py':
            # Import module và đăng ký Blueprint
            module_name = f'app.routes.{filename[:-3]}'
            module = importlib.import_module(module_name)
            for attr in dir(module):
                blueprint = getattr(module, attr)
                if isinstance(blueprint, Blueprint):
                    # Đăng ký Blueprint với tên duy nhất
                    app.register_blueprint(blueprint, name=f"{blueprint.name}_{filename[:-3]}")

# Đăng ký Blueprints cho ứng dụng Flask
register_blueprints(app)


@login_manager.user_loader
def load_user(user_id):
    admin_account = AdminAccount.query.get(user_id)
    if admin_account:
        return admin_account
    
    teacher_account = TeacherAccount.query.get(user_id)
    if teacher_account:
        return teacher_account
    
    student_account = StudentAccount.query.get(user_id)
    if student_account:
        return student_account
    return None




