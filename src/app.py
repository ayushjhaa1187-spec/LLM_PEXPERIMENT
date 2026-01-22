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

from src.llm_engine import MultiAgentRAGSystem
from src.llm_engine.policy_analyzer import FARPolicyAnalyzer
from src.llm_engine.cost_calculator import GovernmentCostCalculator

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://user:password@localhost:5432/llm_consulting'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-key-change-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Initialize LLM system
rag_system = MultiAgentRAGSystem()
policy_analyzer = FARPolicyAnalyzer()
cost_calculator = GovernmentCostCalculator()


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
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


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


class Analysis(db.Model):
    """Analysis results model"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    analysis_type = db.Column(db.String(50))
    results = db.Column(db.JSON)
    confidence_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# AUTHENTICATION ROUTES

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing fields'}), 400
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'User exists'}), 409
        
        user = User(
            username=data['username'],
            email=data['email'],
            agency=data.get('agency'),
            role='analyst'
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'Success'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login and get JWT token"""
    try:
        data = request.get_json()
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Missing credentials'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        if not user or not user.check_password(data['password']) or not user.active:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        access_token = create_access_token(
            identity={'id': user.id, 'username': user.username, 'role': user.role}
        )
        return jsonify({'access_token': access_token, 'user': {
            'id': user.id, 'username': user.username, 'email': user.email,
            'agency': user.agency, 'role': user.role
        }}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# PROJECT ROUTES

@app.route('/api/projects', methods=['GET'])
@jwt_required()
def get_projects():
    """Get user projects"""
    try:
        user_id = get_jwt_identity()['id']
        projects = Project.query.filter_by(created_by=user_id).all()
        return jsonify({'projects': [{
            'id': p.id, 'project_id': p.project_id, 'title': p.title,
            'agency': p.agency, 'budget': p.budget, 'status': p.status,
            'created_at': p.created_at.isoformat()
        } for p in projects]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects', methods=['POST'])
@jwt_required()
def create_project():
    """Create project"""
    try:
        user_id = get_jwt_identity()['id']
        data = request.get_json()
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
        return jsonify({'message': 'Created', 'project_id': project.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ANALYSIS ROUTES

@app.route('/api/analyze/policy/<int:project_id>', methods=['POST'])
@jwt_required()
def analyze_policy(project_id):
    """Policy analysis"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Not found'}), 404
        
        project_data = {
            'project_id': project.project_id,
            'agency': project.agency,
            'budget': f"${project.budget/1e6:.1f}M",
            'description': project.description
        }
        analyses = policy_analyzer.analyze_project(project_data)
        report = policy_analyzer.generate_compliance_report(analyses)
        
        analysis = Analysis(project_id=project_id, analysis_type='policy',
                          results=report, confidence_score=report.get('confidence_in_estimates', 0))
        project.status = 'analysis'
        db.session.add(analysis)
        db.session.commit()
        return jsonify(report), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze/cost/<int:project_id>', methods=['POST'])
@jwt_required()
def analyze_cost(project_id):
    """Cost analysis"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Not found'}), 404
        
        project_data = {
            'project_id': project.project_id,
            'agency': project.agency,
            'budget': f"${project.budget/1e6:.1f}M"
        }
        report = cost_calculator.generate_cost_comparison_report(project_data)
        analysis = Analysis(project_id=project_id, analysis_type='cost',
                          results=report, confidence_score=report.get('confidence_in_estimates', 0))
        db.session.add(analysis)
        db.session.commit()
        return jsonify(report), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
