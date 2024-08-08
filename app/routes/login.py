from flask import request, session, flash, render_template, redirect, url_for, Blueprint
from app import db, AdminAccount, TeacherAccount, StudentAccount
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_login import login_user, current_user
login_bp = Blueprint('login', __name__)
@login_bp.route("/login", methods = ["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home_home.home"))
    
    if request.method == "POST":
        user_name = request.form["id"]
        password = request.form["password"]

        userStudent = StudentAccount.query.get(user_name)
        if userStudent and userStudent.check_password(password):
            login_user(userStudent)            
            flash("You Logged in successfully!!!", "info")
            return redirect(url_for("home_home.home"))


        userAdmin = AdminAccount.query.get(user_name)
        if userAdmin and userAdmin.check_password(password):
            login_user(userAdmin)            
            flash("You Logged in successfully!!!", "info")
            return redirect(url_for("home_home.home"))
                    
        userTeacher = TeacherAccount.query.get(user_name)
        if userTeacher and userTeacher.check_password(password):
            login_user(userTeacher)            
            flash("You Logged in successfully!!!", "info")
            return redirect(url_for("home_home.home"))
        
       
        flash("Invalid credentials! Please try again.", "info")

    
    return render_template('login.html') 