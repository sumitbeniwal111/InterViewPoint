# app/routes/interview.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from datetime import datetime, timezone
from app import db
from app.models import InterviewExperience, User
from app.__init__ import ROLE_ADMIN, ROLE_STUDENT
from functools import wraps
from sqlalchemy import or_ # NEW: Import or_ for OR conditions in filter

interview_bp = Blueprint('interview', __name__)

# Helper function to check for admin role
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != ROLE_ADMIN:
            flash('Unauthorized access. Admin privileges required.', 'danger')
            return redirect(url_for('student.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- Student Routes ---

@interview_bp.route('/submit_experience', methods=['GET', 'POST'])
@login_required
def submit_experience():
    if current_user.role != ROLE_STUDENT:
        flash('Only students can submit interview experiences.', 'danger')
        return redirect(url_for('index'))

    form_data = {
        'company_name': request.form.get('company_name', ''),
        'role': request.form.get('role', ''),
        'experience_type': request.form.get('experience_type', ''),
        'batch_year': request.form.get('batch_year', ''),
        'branch': request.form.get('branch', ''),
        'interview_date': request.form.get('interview_date', ''),
        'experience_text': request.form.get('experience_text', ''),
        'rounds_details': request.form.get('rounds_details', '')
    }

    if request.method == 'POST':
        company_name = form_data['company_name']
        role = form_data['role']
        experience_type = form_data['experience_type']
        batch_year_str = form_data['batch_year']
        branch = form_data['branch']
        interview_date_str = form_data['interview_date']
        experience_text = form_data['experience_text']
        rounds_details = form_data['rounds_details']

        if not all([company_name, role, experience_type, experience_text]):
            flash('Please fill in all required fields (Company Name, Role, Experience Type, Experience Text).', 'danger')
            return render_template('submit_experience.html', **form_data)

        batch_year = int(batch_year_str) if batch_year_str and batch_year_str.isdigit() else None
        
        interview_date = None
        if interview_date_str:
            try:
                interview_date = datetime.strptime(interview_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid Interview Date format. Please use YYYY-MM-DD.', 'danger')
                return render_template('submit_experience.html', **form_data)

        new_experience = InterviewExperience(
            user_id=current_user.id,
            company_name=company_name,
            role=role,
            experience_type=experience_type,
            batch_year=batch_year,
            branch=branch,
            interview_date=interview_date,
            experience_text=experience_text,
            rounds_details=rounds_details,
            status='pending'
        )
        db.session.add(new_experience)
        db.session.commit()
        flash('Your interview experience has been submitted for review. Thank you!', 'success')
        return redirect(url_for('interview.view_interview_experiences'))
    
    return render_template('submit_experience.html', **form_data)


@interview_bp.route('/interview_experiences', methods=['GET'])
@login_required
def view_interview_experiences():
    # Get universal search query from the request
    search_query = request.args.get('search', '').strip()

    # Base query for approved experiences
    experiences_query = InterviewExperience.query.filter_by(status='approved')

    # Apply universal search filter if provided
    if search_query:
        # Use OR conditions to search across multiple fields
        experiences_query = experiences_query.filter(
            or_(
                InterviewExperience.company_name.ilike(f'%{search_query}%'),
                InterviewExperience.role.ilike(f'%{search_query}%'),
                InterviewExperience.experience_type.ilike(f'%{search_query}%'),
                # For integer/nullable fields, convert search_query to string for ilike comparison
                db.cast(InterviewExperience.batch_year, db.String).ilike(f'%{search_query}%'),
                InterviewExperience.branch.ilike(f'%{search_query}%')
            )
        )

    # Order the results
    approved_experiences = experiences_query.order_by(InterviewExperience.date_submitted.desc()).all()

    # No need to fetch unique values for dropdowns anymore with universal search
    # These parameters are still passed but will be empty lists/unused in the template
    unique_companies = []
    unique_roles = []
    unique_experience_types = []
    unique_batch_years = []
    unique_branches = []


    return render_template('view_interview_experiences.html',
                           experiences=approved_experiences,
                           unique_companies=unique_companies, # Still pass, but will be empty
                           unique_roles=unique_roles,         # Still pass, but will be empty
                           unique_experience_types=unique_experience_types, # Still pass, but will be empty
                           unique_batch_years=unique_batch_years, # Still pass, but will be empty
                           unique_branches=unique_branches,     # Still pass, but will be empty
                           current_search=search_query) # Pass current search query to pre-fill the form


@interview_bp.route('/interview_experiences/<int:exp_id>')
@login_required
def interview_experience_detail(exp_id):
    experience = InterviewExperience.query.get_or_404(exp_id)
    if experience.status != 'approved' and not (current_user.role == ROLE_ADMIN or experience.user_id == current_user.id):
        flash('You do not have permission to view this experience.', 'danger')
        return redirect(url_for('interview.view_interview_experiences'))
    
    return render_template('interview_experience_detail.html', experience=experience)


# --- Admin Routes (remain unchanged) ---
@interview_bp.route('/admin/manage_interviews')
@admin_required
def admin_manage_interviews():
    # Admins can see all experiences, regardless of status
    all_experiences = InterviewExperience.query.order_by(InterviewExperience.date_submitted.desc()).all()
    return render_template('admin_manage_interviews.html', experiences=all_experiences)


@interview_bp.route('/admin/approve_interview/<int:exp_id>')
@admin_required
def admin_approve_interview(exp_id):
    experience = InterviewExperience.query.get_or_404(exp_id)
    experience.status = 'approved'
    db.session.commit()
    flash(f'Interview experience for {experience.company_name} by {experience.author.email} has been approved.', 'success')
    return redirect(url_for('interview.admin_manage_interviews'))


@interview_bp.route('/admin/reject_interview/<int:exp_id>')
@admin_required
def admin_reject_interview(exp_id):
    experience = InterviewExperience.query.get_or_404(exp_id)
    experience.status = 'rejected'
    db.session.commit()
    flash(f'Interview experience for {experience.company_name} by {experience.author.email} has been rejected.', 'warning')
    return redirect(url_for('interview.admin_manage_interviews'))


@interview_bp.route('/admin/delete_interview/<int:exp_id>')
@admin_required
def admin_delete_interview(exp_id):
    experience = InterviewExperience.query.get_or_404(exp_id)
    company_name = experience.company_name
    user_email = experience.author.email
    db.session.delete(experience)
    db.session.commit()
    flash(f'Interview experience for {company_name} by {user_email} has been permanently deleted.', 'info')
    return redirect(url_for('interview.admin_manage_interviews'))