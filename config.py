# config.py
import os

class Config:
    # Flask Secret Key for session security, flash messages, etc.
    # This should be a plain STRING here. It will be encoded to bytes in app/__init__.py
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_super_secret_key_for_your_college_portal_simplified'

    # Database Configuration (PostgreSQL)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    else:
        # Local PostgreSQL for development (replace with your user/password/db)
        SQLALCHEMY_DATABASE_URI = 'postgresql://student_notes_user:Sumit%401234@localhost:5432/interview_db'
        # Or uncomment for SQLite local development if preferred (but aim for PG)
        # SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail Configuration for Password Reset
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    
    # CORRECTED LOGIC for MAIL_USE_TLS and MAIL_USE_SSL
    # They should be boolean True/False based on environment variable string 'true' or 'false'
    # Default to True for TLS (common port 587) and False for SSL
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'sumitbeniwal906@gmail.com'
    # CRITICAL: DO NOT HARDCODE PASSWORD HERE. Remove the default value.
    # It *must* be an environment variable in production.
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Enable Flask-Mail debug output for testing. REMOVE OR SET TO FALSE FOR PRODUCTION
    MAIL_DEBUG = True
