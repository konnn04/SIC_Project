
import os
from flask import Flask, Blueprint

from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask_socketio import SocketIO
import importlib
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

def init_db():
    with app.app_context():
        db.create_all()        
        print("Các bảng cơ sở dữ liệu đã được tạo.")

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    svname = db.Column(db.String(100), nullable=False)
    mssv = db.Column(db.String(20), unique=True, nullable=False)

    def __repr__(self):
        return f'<Student {self.svname}>'

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