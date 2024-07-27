from flask import request, session, flash, render_template, redirect, url_for, Blueprint

login_bp = Blueprint('login', __name__)
@login_bp.route("/login", methods = ["POST", "GET"])
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
            return redirect(url_for("login_login.login"))
    if "user" in session:
        name = session["user"]
        flash("You have already logged in!!!", "info")
        return render_template("user.html", user=name)
    return render_template('login.html') 