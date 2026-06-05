"""Authentication routes for USP Summarization System"""
from functools import wraps
from flask import (
    Blueprint, render_template,
    request, redirect, url_for,
    session, flash
)
from werkzeug.security import check_password_hash
from models.user import User

auth = Blueprint('auth', __name__)

def login_required(f):
    """Decorator to protect routes that require login"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.','error')
            return redirect(url_for('auth.login'))
        return f(*args,**kwargs)
    return decorated

@auth.route('/')
def home():
    """Redirect to dashboard or login"""
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle USP LMS login"""
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            session['user_name'] = user.name
            session['username'] = user.username
            session['department'] = user.department
            session['semester'] = user.semester
            flash(f'Welcome, {user.name}!', 'success')
            return redirect(url_for('auth.dashboard'))
        flash('Invalid USP username or password.', 'error')
        return render_template('login.html')
    return render_template('login.html')
@auth.route('/dashboard')
def dashboard():
    """Show user Dashboard"""
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html',
        name=session.get('user_name'),
        username=session.get('username'),
        department=session.get('department'),
        semester=session.get('semester')
    )
@auth.route('/logout')
def logout():
    """Clear session and logout"""
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))
