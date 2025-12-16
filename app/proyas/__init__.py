from flask import Blueprint

proyas_bp = Blueprint('proyas', __name__)

from app.proyas import routes
