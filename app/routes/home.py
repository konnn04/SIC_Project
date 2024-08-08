from flask import Blueprint, render_template
from flask_login import login_required, current_user
home_bp = Blueprint('home', __name__)

@home_bp.route('/home')
@login_required
def home():
    return render_template('home.html',name= current_user.id)

@home_bp.route('/unauthorized')
def unauthorized():
    return 'You are not authorized to view this page.', 403