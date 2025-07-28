# app/models.py
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta
import secrets
import hashlib
from flask import current_app # To access app config for SECRET_KEY

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), nullable=False)

    interview_experiences = db.relationship('InterviewExperience', backref='author', lazy=True)
    reset_tokens = db.relationship('ResetToken', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self, expires_sec=1800):
        # Generate a simple secure token
        token = secrets.token_urlsafe(32)
        return token

    @staticmethod
    def verify_reset_token(token):
        # Find the reset token in the database
        reset_token = ResetToken.query.filter_by(token=token).first()
        if reset_token:
            # Ensure both datetimes are timezone-aware for comparison
            current_time = datetime.now(timezone.utc)
            expires_at = reset_token.expires_at
            if expires_at.tzinfo is None:
                # If expires_at is naive, assume it's UTC
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at > current_time:
                return User.query.get(reset_token.user_id)
        return None

    def __repr__(self):
        return f"User('{self.email}', '{self.role}')"

class InterviewExperience(db.Model):
    __tablename__ = 'interview_experience'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    experience_type = db.Column(db.String(50), nullable=False)
    batch_year = db.Column(db.Integer)
    branch = db.Column(db.String(100))
    interview_date = db.Column(db.Date)
    date_submitted = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    experience_text = db.Column(db.Text, nullable=False)
    rounds_details = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending', nullable=False)

    def __repr__(self):
        return f"<InterviewExperience {self.company_name} - {self.role} by {self.author.email}>"

class ResetToken(db.Model):
    __tablename__ = 'reset_token'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(120), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<ResetToken {self.token} for User {self.user_id}>"