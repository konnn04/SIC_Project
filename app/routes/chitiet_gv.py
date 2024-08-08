from app import db, Teacher, Class, Label, TeacherInClass
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_login import login_required, current_user
from tool import get_role

chitiet_gv_bp = Blueprint('chitiet_gv', __name__)

@chitiet_gv_bp.route('/chitiet_gv/<string:teacher_id>', methods=[ "POST","GET"])
@login_required
def chitiet_gv(teacher_id): 
    teacher = Teacher.query.filter_by(idTeacher=teacher_id).first()
    joined_classes = TeacherInClass.query.filter_by(idTeacher=teacher.idTeacher).all()
    unjoin_classes = Class.query.filter(Class.idClass.notin_([c.idClass for c in joined_classes])).all()
    if teacher is None:
        flash("Không tìm thấy giảng viên!")
        return redirect(url_for("thongtin_thongtin.thongtin"))
    return render_template('chitiet_gv.html', teacher=teacher, joined_class=joined_classes, unjoin_class = unjoin_classes)

@chitiet_gv_bp.route('/save_gv/<string:teacher_id>', methods=["POST","GET"])
@login_required
def save_gv(teacher_id):
    if (get_role()!= "admin"):
        flash("Bạn không có quyền truy cập trang này!")
        return redirect(url_for("home_home.home"))
    teacher = teacher.query.filter_by(idTeacher=teacher_id).first()
    if teacher is None:
        flash("Không tìm thấy giảng viên này!")
        return redirect(url_for("thongtin_thongtin.thongtin"))
    return redirect(url_for("chitiet_gv_chitiet_gv.chitiet_gv", teacher_id=teacher_id))

@chitiet_gv_bp.route('/delete_gv_class/<string:teacher_id>/<string:class_id>', methods=["POST"])
@login_required
def delete_gv_class(teacher_id,class_id):
    if (get_role()!= "admin"):
        flash("Bạn không có quyền truy cập trang này!")
        return redirect(url_for("home_home.home"))
    TeacherInClass.query.filter_by(idTeacher=teacher_id, idClass=class_id).delete()
    db.session.commit()
    flash("Xóa thành công!")
    return redirect(url_for("chitiet_gv_chitiet_gv.chitiet_gv", teacher_id=teacher_id))
    

@chitiet_gv_bp.route('/add_gv_class/<string:teacher_id>', methods=["POST"])
@login_required
def add_gv_class(teacher_id):
    if (get_role()!= "admin"):
        flash("Bạn không có quyền truy cập trang này!")
        return redirect(url_for("home_home.home"))
    teacher_class = TeacherInClass(idTeacher=teacher_id, idClass=request.form['add_class'])
    db.session.add(teacher_class)
    db.session.commit()
    flash("Thêm thành công!")
    return redirect(url_for("chitiet_gv_chitiet_gv.chitiet_gv", teacher_id=teacher_id))
