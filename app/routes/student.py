# app/routes/student.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
# Removed imports for secure_filename, Note, PYQ as file uploads and notes/pyqs are removed
from ..models import User # Only User model needed for current_user check
from .. import db, ROLE_STUDENT, ROLE_ADMIN # Import roles
from functools import wraps

student_bp = Blueprint('student', __name__)

# Decorator to ensure only logged-in students or admins can access restricted routes
def student_or_admin_required(f):
    @login_required
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or \
           (current_user.role != ROLE_STUDENT and current_user.role != ROLE_ADMIN):
            flash('Access denied. Please log in to view this content.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# STUDENT DASHBOARD - Simplified to only remaining features
@student_bp.route('/dashboard')
@student_or_admin_required
def dashboard():
    return render_template('student_dashboard.html')

# --- REMOVED: All Note Browse, Upload, Download Routes ---
# --- REMOVED: All PYQ Browse, Upload, Download Routes ---
# This includes removal of /browse_notes, /download_note, /browse_pyqs, /download_pyq routes

# Profile page - unchanged (assuming basic user profile display)
@student_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

# Publicly Accessible Routes - unchanged
@student_bp.route('/about_us')
def about_us():
    return render_template('about.html')

@student_bp.route('/contact_us')
def contact_us():
    return render_template('contact.html')

@student_bp.route('/services')
def services():
    return render_template('services.html')