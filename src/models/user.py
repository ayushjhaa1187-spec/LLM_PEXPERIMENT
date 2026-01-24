from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from src import db

class User(db.Model):
    """
    User model for authentication and role-based access control.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    agency = db.Column(db.String(120))
    role = db.Column(db.String(50), default='analyst')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    projects = db.relationship('Project', backref='author', lazy=True)
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check the password against the stored hash."""
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        """Return a JSON-serializable dictionary representation of the user."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'agency': self.agency,
            'role': self.role,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def __repr__(self):
        return f'<User {self.username}>'
