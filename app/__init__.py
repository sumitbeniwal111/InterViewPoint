# app/__init__.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
import os

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()

ROLE_ADMIN = 'admin'
ROLE_STUDENT = 'student'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Set the secret key (Flask will handle encoding internally)
    app.secret_key = app.config['SECRET_KEY']

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    mail.init_app(app)

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.student import student_bp
    from .routes.interview import interview_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(interview_bp, url_prefix='/interviews')

    @app.route('/')
    def index():
        return render_template('index.html')

    # IMPORTANT: db.create_all() is commented out because Flask-Migrate handles schema creation/updates
    # with app.app_context():
    #    db.create_all()

    return app