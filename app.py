from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///volunteers.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    registrations = db.relationship('VolunteerRegistration', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    start_time = db.Column(db.String(8))  # Format: HH:MM
    end_time = db.Column(db.String(8))    # Format: HH:MM
    location = db.Column(db.String(200))
    max_volunteers = db.Column(db.Integer)
    registrations = db.relationship('VolunteerRegistration', backref='activity', lazy=True)

class VolunteerRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    activities = Activity.query.all()
    return render_template('index.html', activities=activities)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('signup'))
        
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/register/<int:activity_id>', methods=['GET', 'POST'])
def register(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    
    # Check if user is already registered
    if current_user.is_authenticated:
        existing_registration = VolunteerRegistration.query.filter_by(
            user_id=current_user.id,
            activity_id=activity.id
        ).first()
        if existing_registration:
            flash('You have already registered for this activity!', 'warning')
            return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = None
        if current_user.is_authenticated:
            user = current_user
        else:
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(email=email)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
            elif not user.check_password(password):
                flash('Invalid password for existing email', 'danger')
                return redirect(url_for('register', activity_id=activity_id))
        
        registration = VolunteerRegistration(user_id=user.id, activity_id=activity.id)
        db.session.add(registration)
        db.session.commit()
        
        flash('Registration submitted successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html', activity=activity)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    activities = Activity.query.all()
    registrations = VolunteerRegistration.query.all()
    return render_template('admin.html', activities=activities, registrations=registrations)

@app.route('/admin/activity/new', methods=['GET', 'POST'])
@login_required
def new_activity():
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date_str = request.form.get('date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        location = request.form.get('location')
        max_volunteers = request.form.get('max_volunteers')
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            activity = Activity(
                title=title,
                description=description,
                date=date,
                start_time=start_time,
                end_time=end_time,
                location=location,
                max_volunteers=int(max_volunteers) if max_volunteers else None
            )
            db.session.add(activity)
            db.session.commit()
            flash('Activity created successfully!', 'success')
            return redirect(url_for('admin'))
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD', 'danger')
    
    return render_template('new_activity.html')

@app.route('/admin/approve/<int:registration_id>')
@login_required
def approve_registration(registration_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    registration = VolunteerRegistration.query.get_or_404(registration_id)
    registration.status = 'approved'
    db.session.commit()
    flash('Registration approved!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/reject/<int:registration_id>')
@login_required
def reject_registration(registration_id):
    if not current_user.is_admin:
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    registration = VolunteerRegistration.query.get_or_404(registration_id)
    registration.status = 'rejected'
    db.session.commit()
    flash('Registration rejected!', 'success')
    return redirect(url_for('admin'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

def create_initial_activities():
    activities = [
        {
            'title': 'Awareness Booth at Tel Aviv University',
            'description': 'Setting up a booth to distribute flyers, answer questions, and engage with students about the hostages\' situation.',
            'date': datetime(2025, 4, 25),
            'start_time': '11:00',
            'end_time': '14:00',
            'location': 'Tel Aviv University Campus',
            'max_volunteers': 10
        },
        {
            'title': 'Volunteer Visit to Hostage Families',
            'description': 'A small group of volunteers will visit families of the hostages to offer emotional support and assistance with errands or logistics.',
            'date': datetime(2025, 4, 27),
            'start_time': '16:00',
            'end_time': '18:00',
            'location': 'Various locations (to be assigned)',
            'max_volunteers': 5
        },
        {
            'title': 'Evening Rally and Candlelight Vigil in Jerusalem',
            'description': 'Participate in an organized rally and vigil to show solidarity and raise public awareness. Volunteers will help with setup, crowd guidance, and cleanup.',
            'date': datetime(2025, 4, 30),
            'start_time': '19:30',
            'end_time': '21:30',
            'location': 'Jerusalem City Center',
            'max_volunteers': 20
        }
    ]
    
    for activity_data in activities:
        if not Activity.query.filter_by(title=activity_data['title']).first():
            activity = Activity(**activity_data)
            db.session.add(activity)
    
    db.session.commit()

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()
        # Create default admin user if it doesn't exist
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(email='admin@example.com', is_admin=True)
            admin.set_password('admin123')  # Change this password in production!
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created with email: admin@example.com and password: admin123")
        
        # Create initial activities
        create_initial_activities()
        print("Initial activities created successfully")

@app.context_processor
def utility_processor():
    def get_registration_status(user_id, activity_id):
        if not user_id:
            return None
        registration = VolunteerRegistration.query.filter_by(
            user_id=user_id,
            activity_id=activity_id
        ).first()
        return registration.status if registration else None
    
    return dict(get_registration_status=get_registration_status)

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 