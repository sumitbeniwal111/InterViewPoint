# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, ResetToken # Import User and ResetToken models
from .. import db, ROLE_ADMIN, ROLE_STUDENT, mail # Import 'db', roles, and 'mail' instance
from functools import wraps
from flask_mail import Message # For sending emails
from datetime import datetime, timedelta, timezone # For token expiry

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        if current_user.role == ROLE_ADMIN:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password')

        if not email or not password:
            flash('Email and password are required!', 'danger')
            return render_template('login.html', email=email)

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome, {user.email}!', 'success')
            if user.role == ROLE_ADMIN:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('login.html', email=email)

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('auth.login'))

# NEW: Student Registration Route
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('index')) # Redirect if already logged in

    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Basic validation
        if not email or not password or not confirm_password:
            flash('All fields are required!', 'danger')
            return render_template('register.html', email=email)

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html', email=email)

        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists. Please login or reset your password.', 'danger')
            return render_template('register.html', email=email)
        
        # Create new student user
        new_student = User(email=email, role=ROLE_STUDENT) # New users are students by default
        new_student.set_password(password)
        db.session.add(new_student)
        db.session.commit()
        flash(f'Account created for {email}! You can now log in.', 'success')
        return redirect(url_for('auth.login')) # Redirect to login page after successful registration
    
    return render_template('register.html')


# Forgot Password Route (remains unchanged from previous version)
@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email').strip()
        user = User.query.filter_by(email=email).first()

        if user:
            ResetToken.query.filter_by(user_id=user.id).delete()
            db.session.commit()

            token = user.get_reset_token()
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

            new_reset_token = ResetToken(token=token, user_id=user.id, expires_at=expires_at)
            db.session.add(new_reset_token)
            db.session.commit()

            reset_url = url_for('auth.reset_password', token=token, _external=True)

            msg = Message('Password Reset Request - Student Hub',
                          sender=current_app.config['MAIL_USERNAME'],
                          recipients=[user.email])
            msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request then simply ignore this email and no changes will be made to your password.
This link is valid for 30 minutes.

- The Student Hub Team
'''
            try:
                print(f"DEBUG: Attempting to send email to {user.email}")
                print(f"DEBUG: Mail config - Server: {current_app.config['MAIL_SERVER']}, Port: {current_app.config['MAIL_PORT']}")
                print(f"DEBUG: Mail config - Username: {current_app.config['MAIL_USERNAME']}")
                print(f"DEBUG: Mail config - TLS: {current_app.config['MAIL_USE_TLS']}, SSL: {current_app.config['MAIL_USE_SSL']}")
                mail.send(msg)
                flash('An email has been sent with instructions to reset your password.', 'info')
            except Exception as e:
                print(f"DEBUG: Mail error details: {str(e)}")
                current_app.logger.error(f"Mail send error to {user.email}: {e}")
                flash('Failed to send password reset email. Please check your mail server configuration.', 'danger')
        else:
            flash('If an account exists with that email, a password reset email has been sent.', 'info')
        
        return redirect(url_for('auth.forgot_password'))
    
    return render_template('forgot_password.html')

# Reset Password Route (updated for new token approach)
@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    user = User.verify_reset_token(token)

    if not user:
        flash('That is an invalid or expired token. Please try resetting your password again.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not password or not confirm_password:
            flash('Both password fields are required.', 'danger')
            return render_template('reset_password.html', token=token)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_password.html', token=token)

        user.set_password(password)
        # Delete the used reset token
        reset_token_db = ResetToken.query.filter_by(token=token).first()
        if reset_token_db:
            db.session.delete(reset_token_db)
        db.session.commit()

        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', token=token)