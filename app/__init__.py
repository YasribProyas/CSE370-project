from flask import Flask
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
import os

load_dotenv()

bootstrap = Bootstrap5()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', '1234lalala')
    
    bootstrap.init_app(app)
    
    from app.auth import auth_bp
    from app.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)



    from app.proyas import proyas_bp
    from app.shaj import shaj_bp
    from app.fahim import fahim_bp
    
    app.register_blueprint(proyas_bp)
    app.register_blueprint(shaj_bp)
    app.register_blueprint(fahim_bp)
    
    return app
