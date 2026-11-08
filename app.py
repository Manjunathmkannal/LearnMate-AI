import os
import json
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

# ---------------------------------------------------------------------------
# App & Config
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-prod')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///learnmate.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


# ---------------------------------------------------------------------------
# Global Template Context
# ---------------------------------------------------------------------------
@app.context_processor
def inject_user():
    return {'user': current_user}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    career_goal   = db.Column(db.String(200))
    skills        = db.Column(db.Text)          # JSON string
    is_admin      = db.Column(db.Boolean, default=False)
    joined_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class CourseProgress(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course     = db.Column(db.String(200), nullable=False)
    status     = db.Column(db.String(50), default='not_started')   # not_started / in_progress / completed
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatHistory(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role       = db.Column(db.String(20), nullable=False)   # 'user' | 'assistant'
    message    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------------------------------------------------------------------------
# Database Initialization (Runs on module import for Gunicorn & Flask run)
# ---------------------------------------------------------------------------
with app.app_context():
    db.create_all()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_watsonx_client():
    """Return an IBM watsonx.ai ModelInference client (lazy init)."""
    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference

        credentials = Credentials(
            url=os.getenv('WATSONX_URL', 'https://us-south.ml.cloud.ibm.com'),
            api_key=os.getenv('WATSONX_API_KEY'),
        )
        model = ModelInference(
            model_id="ibm/granite-4-h-small",
            credentials=credentials,
            project_id=os.getenv('WATSONX_PROJECT_ID'),
            params={
                "decoding_method": "greedy",
                "max_new_tokens": 512,
                "min_new_tokens": 1,
            }
        )
        return model
    except Exception as e:
        app.logger.error(f"watsonx client error: {e}")
        return None


# ---------------------------------------------------------------------------
# Routes – Auth
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        error = None
        if not name or not email or not password:
            error = 'All fields are required.'
        elif password != confirm:
            error = 'Passwords do not match.'
        elif User.query.filter_by(email=email).first():
            error = 'Email already registered.'

        if error:
            flash(error, 'danger')
        else:
            user = User(name=name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Account created! Complete your profile to get started.', 'success')
            return redirect(url_for('onboarding'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user     = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember'))
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ---------------------------------------------------------------------------
# Routes – Admin Dashboard
# ---------------------------------------------------------------------------
@app.route('/admin/users')
@login_required
def admin_users():
    if not getattr(current_user, 'is_admin', False):
        abort(403)

    users = User.query.order_by(User.joined_at.desc()).all()
    user_list = []
    for u in users:
        parsed_skills = []
        if u.skills:
            try:
                parsed_skills = json.loads(u.skills)
            except Exception:
                parsed_skills = []
        user_list.append({
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'career_goal': u.career_goal or 'Not set',
            'skills': parsed_skills,
            'is_admin': u.is_admin,
            'joined_at': u.joined_at.strftime('%Y-%m-%d %H:%M') if u.joined_at else 'N/A'
        })

    return render_template('admin_users.html', users=user_list)


# ---------------------------------------------------------------------------
# Routes – Onboarding
# ---------------------------------------------------------------------------
@app.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    if request.method == 'POST':
        career_goal = request.form.get('career_goal', '').strip()
        skills      = request.form.getlist('skills')
        current_user.career_goal = career_goal
        current_user.skills      = json.dumps(skills)
        db.session.commit()
        flash('Profile updated! Your personalized roadmap is ready.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('onboarding.html')


# ---------------------------------------------------------------------------
# Routes – Dashboard
# ---------------------------------------------------------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    skills = []
    if current_user.skills:
        try:
            skills = json.loads(current_user.skills)
        except Exception:
            pass

    progress = CourseProgress.query.filter_by(user_id=current_user.id).all()
    completed = sum(1 for p in progress if p.status == 'completed')
    in_progress = sum(1 for p in progress if p.status == 'in_progress')

    return render_template(
        'dashboard.html',
        skills=skills,
        progress=progress,
        completed=completed,
        in_progress=in_progress,
        total=len(progress),
    )


# ---------------------------------------------------------------------------
# Routes – Roadmap
# ---------------------------------------------------------------------------
@app.route('/roadmap')
@login_required
def roadmap():
    return render_template('roadmap.html')


# ---------------------------------------------------------------------------
# Routes – Courses
# ---------------------------------------------------------------------------
@app.route('/courses')
@login_required
def courses():
    return render_template('courses.html')


# ---------------------------------------------------------------------------
# Routes – Chatbot (AI)
# ---------------------------------------------------------------------------
@app.route('/chatbot')
@login_required
def chatbot():
    history = ChatHistory.query.filter_by(user_id=current_user.id)\
                               .order_by(ChatHistory.created_at)\
                               .all()
    return render_template('chatbot.html', history=history)


@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    data    = request.get_json()
    message = (data or {}).get('message', '').strip()
    if not message:
        return jsonify({'error': 'Empty message'}), 400

    skills      = []
    career_goal = current_user.career_goal or 'software engineering'
    if current_user.skills:
        try:
            skills = json.loads(current_user.skills)
        except Exception:
            pass

    db.session.add(ChatHistory(user_id=current_user.id, role='user', message=message))
    db.session.commit()

    skills_str = ', '.join(skills) if skills else 'not specified'
    system_ctx = (
        f"You are LearnMate AI, a helpful and encouraging learning assistant. "
        f"The student's name is {current_user.name}. "
        f"Their career goal is: {career_goal}. "
        f"Their current skills are: {skills_str}. "
        f"Provide concise, actionable, and personalized guidance. "
        f"Recommend specific courses, projects, or resources when relevant."
    )
    full_prompt = f"{system_ctx}\n\nStudent: {message}\nLearnMate AI:"

    model = get_watsonx_client()
    if model:
        try:
            response = model.generate_text(prompt=full_prompt)
            reply    = response.strip() if response else "I'm unable to respond right now. Please try again."
        except Exception as e:
            app.logger.error(f"Granite API error: {e}")
            reply = "I encountered an error connecting to the AI service. Please check your API credentials."
    else:
        reply = (
            "⚠️ AI service is not configured. "
            "Please add your WATSONX_API_KEY and WATSONX_PROJECT_ID to the environment variables."
        )

    db.session.add(ChatHistory(user_id=current_user.id, role='assistant', message=reply))
    db.session.commit()

    return jsonify({'reply': reply})


# ---------------------------------------------------------------------------
# Routes – Progress API
# ---------------------------------------------------------------------------
@app.route('/api/progress', methods=['POST'])
@login_required
def update_progress():
    data   = request.get_json()
    course = (data or {}).get('course', '').strip()
    status = (data or {}).get('status', 'in_progress')

    if not course:
        return jsonify({'error': 'Course name required'}), 400

    record = CourseProgress.query.filter_by(user_id=current_user.id, course=course).first()
    if record:
        record.status     = status
        record.updated_at = datetime.utcnow()
    else:
        record = CourseProgress(user_id=current_user.id, course=course, status=status)
        db.session.add(record)

    db.session.commit()
    return jsonify({'success': True, 'status': status})


# ---------------------------------------------------------------------------
# Routes – Profile
# ---------------------------------------------------------------------------
@app.route('/profile')
@login_required
def profile():
    skills = []
    if current_user.skills:
        try:
            skills = json.loads(current_user.skills)
        except Exception:
            pass
    return render_template('profile.html', skills=skills)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_DEBUG', '0') == '1')