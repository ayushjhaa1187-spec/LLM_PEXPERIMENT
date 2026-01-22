"""Flask Web Application with Authentication and Database
Main application for LLM Government Consulting System
"""
import os
from datetime import timedelta, datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# FIX BUG #1: Import from llm_engine (module is now a proper package with __init__.py)
from src.llm_engine import MultiAgentRAGSystem, ResearchAgent, DraftingAgent, RedTeamAgent, ValidatorAgent
from src.llm_engine.policy_analyzer import FARPolicyAnalyzer
from src.llm_engine.cost_calculator import GovernmentCostCalculator

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-production')

# FIX BUG #2: Database configuration with environment variable fallback
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///llm_consulting.db'  # Use SQLite for development instead of hardcoded PostgreSQL
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-key-change-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# FIX BUG #6: CORS configuration with environment-based origins
CORS(app, resources={r"/api/*": {"origins": os.environ.get('CORS_ORIGINS', 'localhost:3000').split(',')}})

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Initialize LLM system
try:
    rag_system = MultiAgentRAGSystem()
    policy_analyzer = FARPolicyAnalyzer()
    cost_calculator = GovernmentCostCalculator()
except Exception as e:
    print(f"Warning: Could not initialize LLM systems: {e}")
    rag_system = None
    policy_analyzer = None
    cost_calculator = None

# DATABASE MODELS
class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    agency = db.Column(db.String(120))
    role = db.Column(db.String(50), default='analyst')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    projects = db.relationship('Project', backref='created_by_user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to JSON-serializable dict (FIX BUG #7)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'agency': self.agency,
            'role': self.role,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Project(db.Model):
    """Government project model"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    agency = db.Column(db.String(120), nullable=False)
    budget = db.Column(db.Float)
    timeline_months = db.Column(db.Integer)
    status = db.Column(db.String(50), default='draft')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    analyses = db.relationship('Analysis', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to JSON-serializable dict (FIX BUG #7)"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'agency': self.agency,
            'budget': self.budget,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Analysis(db.Model):
    """Analysis results model"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    analysis_type = db.Column(db.String(50))
    results = db.Column(db.JSON)
    confidence_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to JSON-serializable dict (FIX BUG #7)"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'analysis_type': self.analysis_type,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# AUTHENTICATION ROUTES
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing fields'}), 400
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'User exists'}), 409
        
        # FIX BUG #8: Call set_password() method to hash password
        user = User(
            username=data['username'],
            email=data['email'],
            agency=data.get('agency'),
            role='analyst'
        )
        user.set_password(data['password'])  # Hash password before saving
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully', 'user': user.to_dict()}), 201
    except Exception as e:
        # FIX BUG #5: Ensure rollback in all exception paths
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login and get JWT token"""
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Missing credentials'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        if not user or not user.check_password(data['password']) or not user.active:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        access_token = create_access_token(
            identity={'id': user.id, 'username': user.username, 'role': user.role}
        )
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        # FIX BUG #5: Ensure rollback in all exception paths
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# PROJECT ROUTES
# FIX BUG #4: Flask routes are properly separated by HTTP method
@app.route('/api/projects', methods=['GET'])
@jwt_required()
def get_projects():
    """Get user projects"""
    try:
        user_id = get_jwt_identity()['id']
        projects = Project.query.filter_by(created_by=user_id).all()
        return jsonify({
            'projects': [p.to_dict() for p in projects]
        }), 200
    except Exception as e:
        # FIX BUG #5: Ensure rollback in all exception paths
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects', methods=['POST'])
@jwt_required()
def create_project():
    """Create project"""
    try:
        user_id = get_jwt_identity()['id']
        data = request.get_json()
        if not data or not data.get('project_id') or not data.get('title'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        project = Project(
            project_id=data.get('project_id'),
            title=data.get('title'),
            description=data.get('description'),
            agency=data.get('agency'),
            budget=float(data.get('budget', 0)),
            timeline_months=int(data.get('timeline_months', 12)),
            created_by=user_id
        )
        db.session.add(project)
        db.session.commit()
        return jsonify({
            'message': 'Project created successfully',
            'project': project.to_dict()
        }), 201
    except Exception as e:
        # FIX BUG #5: Ensure rollback in all exception paths
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ANALYSIS ROUTES
@app.route('/api/analyze/policy/<int:project_id>', methods=['POST'])
@jwt_required()
def analyze_policy(project_id):
    """Policy analysis"""
    try:
        if not policy_analyzer:
            return jsonify({'error': 'Policy analyzer not initialized'}), 503
        
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        project_data = {
            'project_id': project.project_id,
            'agency': project.agency,
            'budget': f"${project.budget/1e6:.1f}M" if project.budget else "$0M",
            'description': project.description
        }
        analyses = policy_analyzer.analyze_project(project_data)
        report = policy_analyzer.generate_compliance_report(analyses)
        
        analysis = Analysis(
            project_id=project_id,
            analysis_type='policy',
            results=report,
            confidence_score=report.get('confidence_in_estimates', 0)
        )
        project.status = 'analysis'
        db.session.add(analysis)
        db.session.commit()
        return jsonify(report), 200
    except Exception as e:
        # FIX BUG #5: Ensure rollback in all exception paths
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/cost/<int:project_id>', methods=['POST'])
@jwt_required()
def analyze_cost(project_id):
    """Cost analysis"""
    try:
        if not cost_calculator:
            return jsonify({'error': 'Cost calculator not initialized'}), 503
        
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        project_data = {
            'project_id': project.project_id,
            'agency': project.agency,
            'budget': f"${project.budget/1e6:.1f}M" if project.budget else "$0M"
        }
        report = cost_calculator.generate_cost_comparison_report(project_data)
        analysis = Analysis(
            project_id=project_id,
            analysis_type='cost',
            results=report,
            confidence_score=report.get('confidence_in_estimates', 0)
        )
        db.session.add(analysis)
        db.session.commit()
        return jsonify(report), 200
    except Exception as e:
        # FIX BUG #5: Ensure rollback in all exception paths
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
