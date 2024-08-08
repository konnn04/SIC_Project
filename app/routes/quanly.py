from app import db, Student, Class, Label, Teacher, StudentAccount, StudentInClass, TeacherAccount, TeacherInClass
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_login import login_required, current_user
from tool import get_role

quanly_bp = Blueprint('quanly', __name__)

@quanly_bp.route('/quanly', methods=[ "POST","GET"])
@login_required
def quanly():    
    if (get_role()!= "admin"):
        flash("Bạn không có quyền truy cập trang này!")
        return redirect(url_for("home_home.home"))

    
    db_all_students = db.session.query(Student, Label).outerjoin(Label).add_columns(Student.idStudent, Student.fname, Student.lname, Student.sex, Student.dob, Student.address,  Label.dataName).all()
    db_data_teachers = Teacher.query.all()
    db_all_classes = Class.query.all() #Lấy tất cả lớp để hiển thị
    return render_template('quanly.html', students=db_all_students, classes=db_all_classes, teachers = db_data_teachers)
@quanly_bp.route("/add_student", methods = ["POST"])
@login_required
def add_student():
    if (get_role()!= "admin"):
        flash("Bạn không có quyền truy cập trang này!")
        return redirect(url_for("home_home.home"))
    
    query = Student.query.filter_by(idStudent=request.form["student_id"])
    if query.first() is None:
        student_id = request.form["student_id"]
        svfname = request.form["svfname"]
        svlname = request.form["svlname"]
        sex = request.form["sex"]
        birthdate = birthdate = datetime.strptime(request.form["birthdate"], '%Y-%m-%d').date()
        address = request.form["address"]
        
        student = Student(idStudent=student_id, fname=svfname, lname=svlname, sex= sex, dob=birthdate, address=address)
        student_acc = StudentAccount(id = student_id, password = "1")
        db.session.add(student,student_acc)
        db.session.commit()
        flash("Cập nhật thông tin thành công!")
        return redirect(url_for("quanly_quanly.quanly"))
    else:
        flash("Mã sinh viên đã tồn tại!")
        return redirect(url_for("quanly_quanly.quanly"))
    
@quanly_bp.route("/add_teacher", methods = ["POST"])
@login_required
def add_teacher():
    if (get_role()!= "admin"):
        flash("Bạn không có quyền truy cập trang này!")
        return redirect(url_for("home_home.home"))
    
    query = Teacher.query.filter_by(idTeacher=request.form["teacher_id"])
    if query.first() is None:
        teacher_id = request.form["teacher_id"]
        svfname = request.form["svfname"]
        svlname = request.form["svlname"]
        sex = request.form["sex"]
        birthdate = birthdate = datetime.strptime(request.form["birthdate"], '%Y-%m-%d').date()
        address = request.form["address"]
        
        teacher = Teacher(idTeacher=teacher_id, fname=svfname, lname=svlname, sex= sex, dob=birthdate, address=address)
        teacher_acc = TeacherAccount(id = teacher_id, password = '1')
        db.session.add(teacher,teacher_acc)
        db.session.commit()
        flash("Cập nhật thông tin thành công!")
        return redirect(url_for("quanly_quanly.quanly"))
    else:
        flash("Mã gv đã tồn tại!")
        return redirect(url_for("quanly_quanly.quanly"))

@quanly_bp.route("/add_class", methods = ["POST"])
@login_required
def add_class():
    if (get_role()!= "admin"):
        flash("Bạn không có quyền truy cập trang này!")
        return redirect(url_for("home_home.home"))

    query = Class.query.filter_by(idClass=request.form["class_id"])
    if query.first() is None:
        class_id = request.form["class_id"]
        class_name = request.form["class_name"]
        class_ = Class(idClass=class_id, name=class_name)
        db.session.add(class_)
        db.session.commit()
        flash("Cập nhật thông tin thành công!")
        return redirect(url_for("quanly_quanly.quanly"))
    else:
        flash("Mã lớp đã tồn tại!")
        return redirect(url_for("quanly_quanly.quanly"))
@quanly_bp.route('/delete_student/<string:student_id>', methods=["POST"])
@login_required
def delete_student(student_id):
    if (get_role()!= "admin"):
        flash("Bạn không có quyền truy cập trang này!")
        return redirect(url_for("home_home.home"))
    
    student = Student.query.get(student_id)
    if student:
        db.session.delete(student)
        
        s = StudentAccount.query.get(student_id)
        if s:
            db.session.delete(s)
        db.session.commit()
        flash('Sinh viên đã được xóa thành công!!', 'success')
    else:
        flash('Sinh viên không tồn tại!!', 'error')
    return redirect(url_for('quanly_quanly.quanly'))

@quanly_bp.route('/delete_teacher/<string:teacher_id>', methods=["POST"])
@login_required
def delete_teacher(teacher_id):
    if (get_role()!= "admin"):
        flash("Bạn không có quyền truy cập trang này!")
        return redirect(url_for("home_home.home"))
    
    teacher = Teacher.query.get(teacher_id)
    if teacher:
        db.session.delete(teacher)
        s = TeacherAccount.query.get(teacher_id)
        if s:
            db.session.delete(s)
        db.session.commit()
        flash('Sinh viên đã được xóa thành công!!', 'success')
    else:
        flash('Sinh viên không tồn tại!!', 'error')
    return redirect(url_for('quanly_quanly.quanly'))

@quanly_bp.route('/delete_class/<class_id>', methods=["POST"])
@login_required
def delete_class(class_id):
    if (get_role()!= "admin"):
        flash("Bạn không có quyền truy cập trang này!")
        return redirect(url_for("home_home.home"))

    class_ = Class.query.get(class_id)
    if class_:
        db.session.delete(class_)
        db.session.commit()
        flash('Lớp đã được xóa thành công!!', 'success')
    else:
        flash('Lớp không tồn tại!!', 'error')
    return redirect(url_for('quanly_quanly.quanly'))
    