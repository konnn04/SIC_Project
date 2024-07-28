
import os
from flask import Flask, Blueprint

from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask_socketio import SocketIO
import importlib
from flask_migrate import Migrate


# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Khởi tạo SocketIO
socketio = SocketIO(app)

#bao mat
app.config["SECRET_KEY"] = "tri"
app.permanent_session_lifetime = timedelta(minutes=1)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
def init_db():
    with app.app_context():
        db.create_all()        
        print("Các bảng cơ sở dữ liệu đã được tạo.")


class Class(db.Model):
    __tablename__ = 'class'
    class_id = db.Column(db.String(50), primary_key=True)
    class_name = db.Column(db.String(50), nullable=False)
    students = db.relationship('Student', backref='class_', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Class {self.class_name}>'

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True)
    svfname = db.Column(db.String(100), nullable=False)
    svlname = db.Column(db.String(100), nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    class_id = db.Column(db.String(50), db.ForeignKey('class.class_id'), nullable=False)
    
    # Relationship với bảng Class     
    labels = db.relationship('Label', backref='student', cascade='all, delete-orphan', lazy=True)
    student_checkins = db.relationship('StudentCheckIn', backref='student', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<Student {self.svname}>'

class StudentCheckIn(db.Model):
    __tablename__ = 'student_checkin'
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), primary_key=True, nullable=False)
    date = db.Column(db.Date,primary_key=True, nullable=False)
    time = db.Column(db.Time,  nullable=False)

    def __repr__(self):
        return f'<StudentCheckIn {self.student_id} {self.date} {self.time}>'
    
class Label(db.Model):
    __tablename__ = 'label'
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), primary_key=True, nullable=False)
    label_name = db.Column(db.String(50), primary_key=True,nullable=False)

    def __repr__(self):
        return f'<Label {self.label_name}>'

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