from app import db, Student
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

user_bp = Blueprint('user', __name__)

@user_bp.route('/user')
def hello_user():
    if "user" in session:
        name = session["user"]
        return render_template("user.html", user=name)
    else:
        flash("You are not logged in!!!", "info")
        return redirect(url_for("login"))

    
    