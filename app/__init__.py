import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin

db = SQLAlchemy()
login_manager = LoginManager()

from .models import User

@login_manager.user_loader
def load_user(user_id):
    # Retrieve user from the database based on user ID
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    with app.app_context():
        from .auth import auth_bp
        from .control import control_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(control_bp, url_prefix='/control')

        db.create_all()  # Create database tables for our data models
        return app
