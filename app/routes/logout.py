from flask import Blueprint, flash, redirect, url_for
from flask_login import logout_user, login_required
logout_bp = Blueprint('logout', __name__)

@logout_bp.route("/logout")
@login_required
def logout():
    logout_user()   
    return redirect(url_for('login_login.login'))