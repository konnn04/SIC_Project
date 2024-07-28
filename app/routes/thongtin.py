from app import db, Student, Class, Label
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime

thongtin_bp = Blueprint('thongtin', __name__)

@thongtin_bp.route('/thongtin', methods=[ "POST","GET"])
def thongtin():    
    db_all_students = db.session.query(Student, Label).outerjoin(Label).add_columns(Student.student_id, Student.svfname, Student.svlname, Student.sex, Student.birthdate, Student.address, Student.class_id, Label.label_name).all()
    db_all_classes = Class.query.all() #Lấy tất cả lớp để hiển thị
    return render_template('thongtin.html', students=db_all_students, classes=db_all_classes)
@thongtin_bp.route("/add_student", methods = ["POST"])
def add_student():
    query = Student.query.filter_by(student_id=request.form["student_id"])
    if query.first() is None:
        student_id = request.form["student_id"]
        svfname = request.form["svfname"]
        svlname = request.form["svlname"]
        sex = request.form["sex"]
        birthdate = birthdate = datetime.strptime(request.form["birthdate"], '%Y-%m-%d').date()
        address = request.form["address"]
        class_id = request.form["class_id"]
        label_name = request.form["label_name"]
        q_label = Label.query.filter_by(label_name=label_name).first()
        if (label_name != None) and (label_name != ""):
            if q_label is None:
                label = Label(label_name=label_name, student_id=student_id)
                db.session.add(label)
                db.session.commit()
            else:   
                flash("Nhãn đã tồn tại hoặc không hợp lệ!")
                return redirect(url_for("thongtin_thongtin.thongtin"))
        student = Student(student_id=student_id, svfname=svfname, svlname=svlname, sex= sex, birthdate=birthdate, address=address, class_id=class_id)
        db.session.add(student)
        db.session.commit()
        flash("Cập nhật thông tin thành công!")
        return redirect(url_for("thongtin_thongtin.thongtin"))
    else:
        flash("Mã sinh viên đã tồn tại!")
        return redirect(url_for("thongtin_thongtin.thongtin"))
@thongtin_bp.route("/add_class", methods = ["POST"])
def add_class():
    query = Class.query.filter_by(class_id=request.form["class_id"])
    if query.first() is None:
        class_id = request.form["class_id"]
        class_name = request.form["class_name"]
        class_ = Class(class_id=class_id, class_name=class_name)
        db.session.add(class_)
        db.session.commit()
        flash("Cập nhật thông tin thành công!")
        return redirect(url_for("thongtin_thongtin.thongtin"))
    else:
        flash("Mã lớp đã tồn tại!")
        return redirect(url_for("thongtin_thongtin.thongtin"))
@thongtin_bp.route('/delete_student/<int:student_id>', methods=["POST"])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
        flash('Sinh viên đã được xóa thành công!!', 'success')
    else:
        flash('Sinh viên không tồn tại!!', 'error')
    return redirect(url_for('thongtin_thongtin.thongtin'))

@thongtin_bp.route('/delete_class/<class_id>', methods=["POST"])
def delete_class(class_id):
    class_ = Class.query.get(class_id)
    if class_:
        db.session.delete(class_)
        db.session.commit()
        flash('Lớp đã được xóa thành công!!', 'success')
    else:
        flash('Lớp không tồn tại!!', 'error')
    return redirect(url_for('thongtin_thongtin.thongtin'))
    