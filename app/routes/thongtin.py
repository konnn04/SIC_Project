from app import db, Student
from flask import Blueprint, render_template, request, redirect, url_for, flash

thongtin_bp = Blueprint('thongtin', __name__)

@thongtin_bp.route('/thongtin', methods=[ "POST","GET"])
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
    
    