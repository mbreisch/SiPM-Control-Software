import os
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin

db = SQLAlchemy()
login_manager = LoginManager()

print("Initialized SQLAlchemy and LoginManager")

from .models import User

@login_manager.user_loader
def load_user(user_id):
    # Retrieve user from the database based on user ID
    print(f"Loading user with ID: {user_id}")
    user = User.query.get(int(user_id))
    print(f"Loaded user: {user}")
    return user

def create_app():
    print("Creating Flask application")
    app = Flask(__name__)
    print("Flask application created")
    
    app.config.from_object('config.Config')
    print(f"App configuration loaded: {app.config}")

    db.init_app(app)
    print("SQLAlchemy initialized with app")
    
    login_manager.init_app(app)
    print("LoginManager initialized with app")
    
    login_manager.login_view = 'auth.login'
    print(f"Login view set to: {login_manager.login_view}")

    with app.app_context():
        from .auth import auth_bp
        from .control import control_bp
        
        print("Registering blueprints")
        app.register_blueprint(auth_bp)
        print("Auth blueprint registered")
        
        app.register_blueprint(control_bp)
        print("Control blueprint registered with URL prefix '/control'")
        
        db.create_all()  # Create database tables for our data models
        print("Database tables created")

        return app
        print("Flask application setup completed")

