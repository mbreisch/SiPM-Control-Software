import os
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin

db = SQLAlchemy()
login_manager = LoginManager()

print("Initialized SQLAlchemy and LoginManager")
time.sleep(5)

from .models import User

@login_manager.user_loader
def load_user(user_id):
    # Retrieve user from the database based on user ID
    print(f"Loading user with ID: {user_id}")
    time.sleep(5)
    user = User.query.get(int(user_id))
    print(f"Loaded user: {user}")
    time.sleep(5)
    return user

def create_app():
    print("Creating Flask application")
    time.sleep(5)
    app = Flask(__name__)
    print("Flask application created")
    time.sleep(5)
    
    app.config.from_object('config.Config')
    print(f"App configuration loaded: {app.config}")
    time.sleep(5)

    db.init_app(app)
    print("SQLAlchemy initialized with app")
    time.sleep(5)
    
    login_manager.init_app(app)
    print("LoginManager initialized with app")
    time.sleep(5)
    
    login_manager.login_view = 'auth.login'
    print(f"Login view set to: {login_manager.login_view}")
    time.sleep(5)

    with app.app_context():
        from .auth import auth_bp
        from .control import control_bp
        
        print("Registering blueprints")
        time.sleep(5)
        app.register_blueprint(auth_bp)
        print("Auth blueprint registered")
        time.sleep(5)
        
        app.register_blueprint(control_bp, url_prefix='/control')
        print("Control blueprint registered with URL prefix '/control'")
        time.sleep(5)

        db.create_all()  # Create database tables for our data models
        print("Database tables created")
        time.sleep(5)

        return app
        print("Flask application setup completed")

