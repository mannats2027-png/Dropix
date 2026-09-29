import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, File
import datetime
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-dropix'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dropix.db'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024 # 500 MB max upload

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Create database tables
with app.app_context():
    db.create_all()
    # Create an admin user if not exists
    if not User.query.filter_by(username='admin').first():
        hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
        admin = User(username='admin', email='admin@dropix.com', password=hashed_password, role='admin')
        db.session.add(admin)
        db.session.commit()

# Context processor for templates
@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now(datetime.timezone.utc)}

# Template filters
@app.template_filter('format_size')
def format_size(size_in_bytes):
    if size_in_bytes is None or size_in_bytes == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} PB"

# ---- ROUTES ----

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember-me'))
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid login credentials', 'error')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
            
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    files = File.query.filter_by(user_id=current_user.id).order_by(File.upload_date.desc()).all()
    
    # Calculate storage
    total_size = sum(f.file_size for f in files)
    storage_limit = 5 * 1024 * 1024 * 1024 # 5GB free limit
    storage_percentage = min(100, (total_size / storage_limit) * 100)
    
    return render_template('dashboard.html', files=files, total_size=total_size, storage_limit=storage_limit, storage_percentage=storage_percentage)

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        abort(403)
        
    total_users = User.query.count()
    total_files = File.query.count()
    
    all_files = File.query.all()
    total_storage = sum(f.file_size for f in all_files)
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_files = File.query.order_by(File.upload_date.desc()).limit(10).all()
    
    return render_template('admin.html', total_users=total_users, total_files=total_files, total_storage=total_storage, recent_users=recent_users, recent_files=recent_files)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('dashboard'))
        
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('dashboard'))
        
    if file:
        original_filename = secure_filename(file.filename) or file.filename or "uploaded_file"
        # Generate a unique filename to prevent overwrites
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        file_size = os.path.getsize(file_path)
        file_type = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'unknown'
        
        new_file = File(
            filename=unique_filename,
            original_filename=original_filename,
            file_size=file_size,
            file_type=file_type,
            user_id=current_user.id
        )
        db.session.add(new_file)
        db.session.commit()
        
        flash('File uploaded successfully', 'success')
        return redirect(url_for('dashboard'))

@app.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    file = db.get_or_404(File, file_id)
    if file.user_id != current_user.id and current_user.role != 'admin':
        abort(403)
        
    return send_from_directory(app.config['UPLOAD_FOLDER'], file.filename, as_attachment=True, download_name=file.original_filename)

@app.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    file = db.get_or_404(File, file_id)
    if file.user_id != current_user.id and current_user.role != 'admin':
        abort(403)
        
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass
        
    db.session.delete(file)
    db.session.commit()
    
    flash('File deleted', 'success')
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/share/<int:file_id>', methods=['POST'])
@login_required
def share_file(file_id):
    file = db.get_or_404(File, file_id)
    if file.user_id != current_user.id:
        abort(403)
        
    share_link = file.generate_share_link()
    return jsonify({'share_url': url_for('shared_file', share_link=share_link, _external=True)})

@app.route('/s/<share_link>')
def shared_file(share_link):
    file = File.query.filter_by(share_link=share_link).first_or_404()
    return render_template('shared.html', file=file)

@app.route('/s/<share_link>/download')
def download_shared(share_link):
    file = File.query.filter_by(share_link=share_link).first_or_404()
    return send_from_directory(app.config['UPLOAD_FOLDER'], file.filename, as_attachment=True, download_name=file.original_filename)

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File size exceeds the 500 MB maximum upload limit.', 'error')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

