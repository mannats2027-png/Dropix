from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime
import uuid

db = SQLAlchemy()

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default='user') # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=utc_now)
    
    files = db.relationship('File', backref='owner', lazy=True)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False) # size in bytes
    file_type = db.Column(db.String(50), nullable=False)
    upload_date = db.Column(db.DateTime, default=utc_now)
    is_public = db.Column(db.Boolean, default=False)
    share_link = db.Column(db.String(100), unique=True, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def generate_share_link(self):
        if not self.share_link:
            self.share_link = str(uuid.uuid4())
            db.session.commit()
        return self.share_link

