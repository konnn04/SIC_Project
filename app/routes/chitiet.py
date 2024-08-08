from app import db, Student, Class, Label, StudentInClass
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_login import login_required, current_user
from tool import get_role

chitiet_bp = Blueprint('chitiet', __name__)

@chitiet_bp.route('/chitiet/<string:student_id>', methods=[ "POST","GET"])
@login_required
def chitiet(student_id): 
    student = Student.query.filter_by(idStudent=student_id).first()
    joined_classes = StudentInClass.query.filter_by(idStudent=student.idStudent).all()
    unjoin_classes = Class.query.filter(Class.idClass.notin_([c.idClass for c in joined_classes])).all()
    if student is None:
        flash("Không tìm thấy sinh viên!")
        return redirect(url_for("thongtin_thongtin.thongtin"))
    return render_template('chitiet.html', student=student, joined_class=joined_classes, unjoin_class = unjoin_classes)

@chitiet_bp.route('/save/<string:student_id>', methods=["POST","GET"])
@login_required
def save(student_id):
    if (get_role()!= "admin"):
        flash("Bạn không có quyền truy cập trang này!")
        return redirect(url_for("home_home.home"))
    student = Student.query.filter_by(idStudent=student_id).first()
    if student is None:
        flash("Không tìm thấy sinh viên!")
        return redirect(url_for("thongtin_thongtin.thongtin"))
    return redirect(url_for("chitiet_chitiet.chitiet", student_id=student_id))

@chitiet_bp.route('/delete_class/<string:student_id>/<string:class_id>', methods=["POST"])
@login_required
def delete_class(student_id,class_id):
    if (get_role()!= "admin"):
        flash("Bạn không có quyền truy cập trang này!")
        return redirect(url_for("home_home.home"))
    StudentInClass.query.filter_by(idStudent=student_id, idClass=class_id).delete()
    db.session.commit()
    flash("Xóa thành công!")
    return redirect(url_for("chitiet_chitiet.chitiet", student_id=student_id))
    

@chitiet_bp.route('/add_class/<string:student_id>', methods=["POST"])
@login_required
def add_class(student_id):
    if (get_role()!= "admin"):
        flash("Bạn không có quyền truy cập trang này!")
        return redirect(url_for("home_home.home"))
    student_class = StudentInClass(idStudent=student_id, idClass=request.form['add_class'])
    db.session.add(student_class)
    db.session.commit()
    flash("Thêm thành công!")
    return redirect(url_for("chitiet_chitiet.chitiet", student_id=student_id))
