from flask import Blueprint

shaj_bp = Blueprint('shaj', __name__)

from app.shaj import routes 
