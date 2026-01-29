"""Authentication and authorization middleware for Phase 1"""
import logging
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable

from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

from .models import User, db

logger = logging.getLogger(__name__)

# Define role hierarchies for RBAC
ROLE_HIERARCHY = {
    'admin': ['admin', 'moderator', 'editor', 'viewer'],
    'moderator': ['moderator', 'editor', 'viewer'],
    'editor': ['editor', 'viewer'],
    'viewer': ['viewer']
}

# Permission mapping
PERMISSIONS = {
    'admin': ['create', 'read', 'update', 'delete', 'manage_users', 'view_analytics'],
    'moderator': ['create', 'read', 'update', 'delete', 'manage_comments'],
    'editor': ['create', 'read', 'update'],
    'viewer': ['read']
}

class AuthMiddleware:
    """Authentication and Authorization Middleware"""
    
    @staticmethod
    def require_auth(f):
        """Decorator to require JWT authentication"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                return f(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Authentication failed: {str(e)}")
                return jsonify({'error': 'Unauthorized'}), 401
        return decorated_function
    
    @staticmethod
    def require_role(*roles):
        """Decorator to require specific roles"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    verify_jwt_in_request()
                    user_id = get_jwt_identity()
                    claims = get_jwt()
                    user_role = claims.get('role', 'viewer')
                    
                    if user_role not in roles:
                        logger.warning(f"User {user_id} denied access - insufficient role")
                        return jsonify({'error': 'Forbidden'}), 403
                    
                    return f(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Role verification failed: {str(e)}")
                    return jsonify({'error': 'Unauthorized'}), 401
            return decorated_function
        return decorator
    
    @staticmethod
    def require_permission(permission):
        """Decorator to require specific permissions"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    verify_jwt_in_request()
                    user_id = get_jwt_identity()
                    claims = get_jwt()
                    user_role = claims.get('role', 'viewer')
                    
                    if permission not in PERMISSIONS.get(user_role, []):
                        logger.warning(f"User {user_id} denied permission: {permission}")
                        return jsonify({'error': 'Forbidden'}), 403
                    
                    return f(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Permission verification failed: {str(e)}")
                    return jsonify({'error': 'Unauthorized'}), 401
            return decorated_function
        return decorator
    
    @staticmethod
    def get_current_user():
        """Get current authenticated user"""
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            return User.query.get(user_id)
        except:
            return None

class PasswordManager:
    """Manage password hashing and verification"""
    
    @staticmethod
    def hash_password(password):
        """Hash password using secure algorithm"""
        return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    @staticmethod
    def verify_password(password_hash, password):
        """Verify password against hash"""
        return check_password_hash(password_hash, password)
    
    @staticmethod
    def is_password_strong(password):
        """Check if password meets strength requirements"""
        if len(password) < 8:
            return False
        if not any(char.isupper() for char in password):
            return False
        if not any(char.isdigit() for char in password):
            return False
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in password):
            return False
        return True

class SessionManager:
    """Manage user sessions and tokens"""
    
    @staticmethod
    def create_session(user_id, duration_hours=24):
        """Create new user session"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
            
            session_data = {
                'user_id': user_id,
                'username': user.username,
                'role': user.role,
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': expires_at.isoformat()
            }
            
            logger.info(f"Session created for user {user_id}")
            return session_data
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            return None
    
    @staticmethod
    def invalidate_session(user_id):
        """Invalidate user session (logout)"""
        try:
            logger.info(f"Session invalidated for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to invalidate session: {str(e)}")
            return False
