# app/routes/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
# Removed User, InterviewExperience, ResetToken imports for student management if not used by interview_experience part directly
from ..models import User, InterviewExperience # Keep User for role check, InterviewExperience for management
from .. import db, ROLE_ADMIN, ROLE_STUDENT
from functools import wraps

admin_bp = Blueprint('admin', __name__)

# Decorator to restrict access to admin users only
def admin_required(f):
    @login_required
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != ROLE_ADMIN:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# ADMIN DASHBOARD - Simplified to only show Interview Experience management
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    return render_template('admin_dashboard.html')

# --- REMOVED: All Student Management Routes ---
# This includes removal of /manage_students, /add_student, /delete_student routes.
# (If your InterviewExperience model needs User or any other model imported here, keep them.
#  I've kept User and InterviewExperience as they are needed by other parts of admin-related code like interview_bp's admin functions.)

# The Interview Experience management routes are in interview.py blueprint and remain unchanged.