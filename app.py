from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User
from blueprints.auth import auth_bp
from blueprints.main import main_bp
from blueprints.pets import pets_bp
from blueprints.profile import profile_bp
import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(pets_bp, url_prefix='/pets')
    app.register_blueprint(profile_bp, url_prefix='/profile')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    # The host='0.0.0.0' is important for Render to correctly map the port.
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
