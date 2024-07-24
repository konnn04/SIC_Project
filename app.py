from flask import Flask, render_template, Response, request, session, flash, redirect, url_for
from flask_socketio import SocketIO
import cv2
import os
import tensorflow.compat.v1 as tf
import random
import src.recognition as recognition
import imutils
import time
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

FRAME = 15

# Load your model here
recognition.start()

app = Flask(__name__)
socketio = SocketIO(app)
#bao mat
app.config["SECRET_KEY"] = "tri"
app.permanent_session_lifetime = timedelta(minutes=1)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    svname = db.Column(db.String(100), nullable=False)
    mssv = db.Column(db.String(20), unique=True, nullable=False)

    def __repr__(self):
        return f'<Student {self.svname}>'
    
def init_db():
    with app.app_context():
        db.create_all()        
        print("Các bảng cơ sở dữ liệu đã được tạo.")

with app.app_context():  
    @app.route("/home")
    @app.route("/")
    def home():
        return render_template('home.html')
    
    @app.route("/thongtin", methods=["POST", "GET"])
    def thongtin():
        if request.method == "POST":
            tensinhvien = request.form["svname"]
            masosinhvien = request.form["mssv"]

            existing = Student.query.filter_by(mssv=masosinhvien).first()
            if existing:
                flash('Mã số sinh viên đã tồn tại !!!', 'error')
            else:
                db_new = Student(svname=tensinhvien, mssv=masosinhvien)
                db.session.add(db_new)
                db.session.commit()
                flash('Sinh viên đã được thêm thành công!!', 'success')
            return redirect(url_for('thongtin'))
        
        db_all = Student.query.all() #Lấy tất cả sinh viên để hiển thị
        return render_template('thongtin.html', students=db_all)


    @app.route('/diemdanh')
    def diemdanh():
        db_all = Student.query.all()  # Lấy tất cả sinh viên để hiển thị
        socketio.start_background_task(target=gen)
        return render_template("diemdanh.html", students=db_all)

    def gen():    
        cap = cv2.VideoCapture(0)              
        while True:
            
            success, frame = cap.read()
            if not success:
                break
            else:           
                frame = cv2.flip(frame, 1)               
                frame = imutils.resize(frame, width=600)

                best_name, best_class_probabilities, frame = recognition.frame_recognition(frame)
                socketio.emit('update_results', {'name': best_name, 'accuracy': best_class_probabilities})
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(.1)
                    

    @app.route('/video_feed')
    def video_feed():    
        return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route("/login", methods = ["POST", "GET"])
    def login():
        if request.method == "POST":
            user_name = request.form["name"]
            password = request.form["password"]
            if user_name and password == "admin":
                session.permanent = True
                session["user"] = user_name
                flash("You Logged in successfully!!!", "info")
                return render_template("user.html", user=user_name)
            else:
                flash("Invalid credentials! Please try again.", "danger")
                return redirect(url_for("login"))
        if "user" in session:
            name = session["user"]
            flash("You have already logged in!!!", "info")
            return render_template("user.html", user=name)
        return render_template('login.html')

    @app.route("/user")
    def hello_user():
        if "user" in session:
            name = session["user"]
            return render_template("user.html", user=name)
        else:
            flash("You are not logged in!!!", "info")
            return redirect(url_for("login"))
        
    @app.route("/logout")
    def log_out():
        flash("You Logged Out!!!", "info")
        session.pop("user", None)
        return redirect(url_for("home"))

    @socketio.on('connect')
    def handle_connect():
        print("Client connected") 

    if __name__ == '__main__':
        # app.run(debug=True, threaded=True)
        init_db()
        socketio.run(app, debug=True)