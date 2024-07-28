from flask import Blueprint, render_template, send_from_directory
import os

static_bp = Blueprint('main', __name__)


@static_bp.route('/static/<path:filename>', methods=['GET'])
def serve_static(filename):
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(os.path.join(root_dir, 'static'), filename)
# 
# Thêm các route khác tại đây