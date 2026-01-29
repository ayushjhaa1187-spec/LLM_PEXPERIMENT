"""Phase 1 API Routes - User Management, Document Management, RAG Queries"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from functools import wraps

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.exc import SQLAlchemyError

from .models import User, Document, Query, AuditLog, db
from .document_processor import DocumentProcessor

# Initialize logger
logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


def audit_action(action_type: str, resource_type: str):
    """Decorator for audit logging"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                user_id = get_jwt_identity() if hasattr(request, 'user') else None
                audit = AuditLog(
                    user_id=user_id,
                    action=action_type,
                    resource_type=resource_type,
                    timestamp=datetime.utcnow(),
                    status='success'
                )
                db.session.add(audit)
                db.session.commit()
                return result
            except Exception as e:
                user_id = get_jwt_identity() if hasattr(request, 'user') else None
                audit = AuditLog(
                    user_id=user_id,
                    action=action_type,
                    resource_type=resource_type,
                    timestamp=datetime.utcnow(),
                    status='error',
                    details=str(e)
                )
                db.session.add(audit)
                db.session.commit()
                raise
        return decorated_function
    return decorator


# ============= USER MANAGEMENT ENDPOINTS =============

@api_bp.route('/auth/register', methods=['POST'])
@limiter.limit("5 per hour")
@audit_action('CREATE', 'USER')
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        user = User(
            username=data['username'],
            email=data['email'],
            role=data.get('role', 'viewer')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=24)
        )
        
        logger.info(f"User registered: {user.id}")
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'access_token': access_token
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error during registration: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/auth/login', methods=['POST'])
@limiter.limit("10 per hour")
@audit_action('LOGIN', 'USER')
def login():
    """User login"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['email', 'password']):
            return jsonify({'error': 'Missing credentials'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=24)
        )
        
        logger.info(f"User logged in: {user.id}")
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'access_token': access_token
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500


@api_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@audit_action('READ', 'USER')
def get_user(user_id):
    """Get user profile"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at.isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        return jsonify({'error': 'Failed to fetch user'}), 500


# ============= DOCUMENT MANAGEMENT ENDPOINTS =============

@api_bp.route('/documents/upload', methods=['POST'])
@jwt_required()
@limiter.limit("50 per hour")
@audit_action('UPLOAD', 'DOCUMENT')
def upload_document():
    """Upload and process document"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        user_id = get_jwt_identity()
        
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Process document
        processor = DocumentProcessor()
        file_content = file.read()
        processed_content = processor.process(file_content, file.filename)
        
        document = Document(
            user_id=user_id,
            filename=file.filename,
            content=processed_content['text'],
            file_type=file.filename.split('.')[-1],
            size=len(file_content),
            status='processed'
        )
        
        db.session.add(document)
        db.session.commit()
        
        logger.info(f"Document uploaded: {document.id} by user {user_id}")
        return jsonify({
            'id': document.id,
            'filename': document.filename,
            'status': document.status,
            'created_at': document.created_at.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Document upload error: {str(e)}")
        return jsonify({'error': 'Upload failed'}), 500


@api_bp.route('/documents', methods=['GET'])
@jwt_required()
@audit_action('LIST', 'DOCUMENT')
def list_documents():
    """List user documents"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        paginated = Document.query.filter_by(user_id=user_id).paginate(
            page=page, per_page=limit
        )
        
        documents = [{
            'id': doc.id,
            'filename': doc.filename,
            'status': doc.status,
            'size': doc.size,
            'created_at': doc.created_at.isoformat()
        } for doc in paginated.items]
        
        return jsonify({
            'documents': documents,
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return jsonify({'error': 'Failed to list documents'}), 500


@api_bp.route('/documents/<int:doc_id>', methods=['GET'])
@jwt_required()
@audit_action('READ', 'DOCUMENT')
def get_document(doc_id):
    """Get document details"""
    try:
        user_id = get_jwt_identity()
        document = Document.query.get(doc_id)
        
        if not document or document.user_id != user_id:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({
            'id': document.id,
            'filename': document.filename,
            'content': document.content[:500],  # First 500 chars
            'status': document.status,
            'size': document.size,
            'created_at': document.created_at.isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching document: {str(e)}")
        return jsonify({'error': 'Failed to fetch document'}), 500


# ============= RAG QUERY ENDPOINTS =============

@api_bp.route('/queries', methods=['POST'])
@jwt_required()
@limiter.limit("30 per hour")
@audit_action('CREATE', 'QUERY')
def create_query():
    """Create and process RAG query"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if not data or 'question' not in data:
            return jsonify({'error': 'Missing question'}), 400
        
        # Retrieve relevant documents (in production, use vector DB)
        relevant_docs = Document.query.filter_by(
            user_id=user_id,
            status='processed'
        ).limit(5).all()
        
        if not relevant_docs:
            return jsonify({'error': 'No documents available for query'}), 404
        
        query = Query(
            user_id=user_id,
            question=data['question'],
            context=[doc.id for doc in relevant_docs],
            status='pending',
            created_at=datetime.utcnow()
        )
        
        db.session.add(query)
        db.session.commit()
        
        # In production, this would call LLM API
        answer = "Answer generated from documents"
        query.answer = answer
        query.status = 'completed'
        db.session.commit()
        
        logger.info(f"Query created: {query.id} by user {user_id}")
        return jsonify({
            'id': query.id,
            'question': query.question,
            'answer': query.answer,
            'status': query.status,
            'created_at': query.created_at.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Query creation error: {str(e)}")
        return jsonify({'error': 'Query failed'}), 500


@api_bp.route('/queries/<int:query_id>', methods=['GET'])
@jwt_required()
@audit_action('READ', 'QUERY')
def get_query(query_id):
    """Get query results"""
    try:
        user_id = get_jwt_identity()
        query = Query.query.get(query_id)
        
        if not query or query.user_id != user_id:
            return jsonify({'error': 'Query not found'}), 404
        
        return jsonify({
            'id': query.id,
            'question': query.question,
            'answer': query.answer,
            'status': query.status,
            'created_at': query.created_at.isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching query: {str(e)}")
        return jsonify({'error': 'Failed to fetch query'}), 500


# ============= HEALTH CHECK =============

@api_bp.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200
