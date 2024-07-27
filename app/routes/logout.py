from flask import Blueprint, session, flash, redirect, url_for

logout_bp = Blueprint('logout', __name__)

logout_bp.route("/logout")
def log_out():
    flash("You Logged Out!!!", "info")
    session.pop("user", None)
    return redirect(url_for("home"))
