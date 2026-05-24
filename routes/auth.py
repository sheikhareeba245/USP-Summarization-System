from flask import (
    Blueprint, render_template,
    request, redirect, url_for,
    session, flash
)
from werkzeug.security import check_password_hash
from models.user import User

auth = Blueprint('auth', __name__)

@auth.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Agar already logged in hai
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validation
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')
        
        # Database mein check karo
        user = User.query.filter_by(
            roll_number=username
        ).first()
        
        # Verify karo
        if user and check_password_hash(user.password, password):
            # Session banao
            session['user_id'] = user.user_id
            session['user_name'] = user.name
            session['username'] = user.roll_number
            session['department'] = user.department
            session['semester'] = user.semester
            
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Invalid USP username or password.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')


@auth.route('/dashboard')
def dashboard():
    # Login check
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
    user_name = session.get('user_name', 'User')
    session.clear()
    flash(f'You have been logged out successfully.', 'success')
    return redirect(url_for('auth.login'))