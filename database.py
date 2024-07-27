from flask import Flask, jsonify, flash, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Class(db.Model):
    __tablename__ = 'class'
    class_id = db.Column(db.String(50), primary_key=True)
    class_name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Class {self.class_name}>'

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    class_id = db.Column(db.String(50), db.ForeignKey('class.class_id'), nullable=False)
    
    class_ = db.relationship('Class', backref=db.backref('students', lazy=True))

    def __repr__(self):
        return f'<Student {self.name}>'

class StudentLabel(db.Model):
    __tablename__ = 'student_label'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    
    student = db.relationship('Student', backref=db.backref('student_labels', lazy=True))

    def __repr__(self):
        return f'<StudentLabel {self.id}>'

with app.app_context():
    db.create_all()

@app.route('/add_class/<class_id>/<class_name>')
def add_class(class_id, class_name):
    existing_class = Class.query.filter_by(class_id=class_id).first()
    if existing_class:
        flash(f'Class with ID {class_id} already exists.', 'error')
        return redirect(url_for('index'))

    new_class = Class(class_id=class_id, class_name=class_name)
    db.session.add(new_class)
    db.session.commit()
    flash(f'Class {class_name} with ID {class_id} has been added.', 'success')
    return redirect(url_for('index'))

@app.route('/add_student/<student_id>/<name>/<birthdate>/<address>/<class_id>')
def add_student(student_id, name, birthdate, address, class_id):
    existing_student = Student.query.filter_by(student_id=student_id).first()
    if existing_student:
        flash(f'Student with ID {student_id} already exists.', 'error')
        return redirect(url_for('index'))

    # Check if the class_id exists
    existing_class = Class.query.filter_by(class_id=class_id).first()
    if not existing_class:
        flash(f'Class with ID {class_id} does not exist.', 'error')
        return redirect(url_for('index'))

    birthdate_obj = datetime.strptime(birthdate, '%Y-%m-%d')
    new_student = Student(student_id=student_id, name=name, birthdate=birthdate_obj, address=address, class_id=class_id)
    db.session.add(new_student)
    db.session.commit()
    flash(f'Student {name} with ID {student_id} has been added.', 'success')
    return redirect(url_for('index'))

@app.route('/add_student_label/<student_id>')
def add_student_label(student_id):
    existing_student = Student.query.filter_by(student_id=student_id).first()
    if not existing_student:
        flash(f'Student with ID {student_id} does not exist.', 'error')
        return redirect(url_for('index'))

    new_label = StudentLabel(student_id=student_id)
    db.session.add(new_label)
    db.session.commit()
    flash(f'Student label for student ID {student_id} has been added.', 'success')
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('base.html')  # Render the base template

if __name__ == '__main__':
    app.run(debug=True)
