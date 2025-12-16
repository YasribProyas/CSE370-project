from flask import Blueprint

# todo: register routes according to features given to you
fahim_bp = Blueprint('fahim', __name__)

from app.fahim import routes
