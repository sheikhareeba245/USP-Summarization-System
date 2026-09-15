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
            flash('Please login first.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@auth.route('/')
def home():
    """Redirect to dashboard or login"""
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle USP LMS login with try-except handling"""
    try:
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

    except Exception as e:
        print(f"Login error encountered: {e}")
        return render_template('login.html')

@auth.route('/dashboard')
def dashboard():
    """Show user Dashboard with Direct Real-Time Counting"""
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')

    # Direct Table Counting Queries with Try-Except
    try:
        from models.document import Document
        doc_count = Document.query.count()
    except Exception as e:
        print(f"Doc count error: {e}")
        doc_count = 0

    try:
        from models.summary import Summary
        summary_count = Summary.query.count()
    except Exception as e:
        print(f"Summary count error: {e}")
        summary_count = 0

    try:
        from models.chat import Chat
        chat_count = Chat.query.count()
    except Exception as e:
        print(f"Chat count error: {e}")
        chat_count = 0

    # Print debug count in terminal to verify
    print(f"--- DASHBOARD STATS -> Docs: {doc_count}, Summaries: {summary_count}, Chats: {chat_count} ---")

    # Render Template
    try:
        return render_template('dashboard.html',
            name=session.get('user_name'),
            username=session.get('username'),
            department=session.get('department'),
            semester=session.get('semester'),
            doc_count=doc_count,
            summary_count=summary_count,
            chat_count=chat_count
        )
    except Exception as e:
        print(f"Dashboard render error: {e}")
        flash(f"Error loading dashboard: {e}", "error")
        return redirect(url_for('auth.login'))

@auth.route('/logout')
def logout():
    """Clear session and logout"""
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))
