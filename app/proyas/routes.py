from flask import render_template
from app.proyas import proyas_bp

@proyas_bp.route('/')
def index():
    return render_template('proyas/index.html')
