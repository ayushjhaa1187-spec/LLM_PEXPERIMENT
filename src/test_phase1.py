"""Phase 1 test suite"""
import pytest
import json
from flask_jwt_extended import create_access_token

from .models import User, Document, Query, db
from .auth_middleware import PasswordManager

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_user(app):
    with app.app_context():
        user = User(
            username='admin_test',
            email='admin@test.com',
            role='admin'
        )
        user.set_password('TestPass123!')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def auth_token(admin_user, app):
    with app.app_context():
        return create_access_token(identity=admin_user.id)

class TestUserAuthentication:
    def test_user_registration_success(self, client):
        response = client.post('/api/v1/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'SecurePass123!'
        })
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'access_token' in data
    
    def test_user_login_success(self, client, admin_user):
        response = client.post('/api/v1/auth/login', json={
            'email': 'admin@test.com',
            'password': 'TestPass123!'
        })
        assert response.status_code == 200
    
    def test_user_login_invalid_credentials(self, client, admin_user):
        response = client.post('/api/v1/auth/login', json={
            'email': 'admin@test.com',
            'password': 'WrongPassword'
        })
        assert response.status_code == 401

class TestDocumentManagement:
    def test_document_list_unauthorized(self, client):
        response = client.get('/api/v1/documents')
        assert response.status_code == 401
    
    def test_document_list_authorized(self, client, auth_token):
        headers = {'Authorization': f'Bearer {auth_token}'}
        response = client.get('/api/v1/documents', headers=headers)
        assert response.status_code == 200

class TestHealthCheck:
    def test_health_check(self, client):
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'

class TestPasswordSecurity:
    def test_password_hashing(self):
        password = 'MySecurePass123!'
        hashed = PasswordManager.hash_password(password)
        assert hashed != password
        assert PasswordManager.verify_password(hashed, password)
    
    def test_password_verification_fails(self):
        password = 'MySecurePass123!'
        hashed = PasswordManager.hash_password(password)
        assert not PasswordManager.verify_password(hashed, 'WrongPassword')
    
    def test_password_strength(self):
        assert PasswordManager.is_password_strong('TestPass123!')
        assert not PasswordManager.is_password_strong('weak')

class TestDatabaseOperations:
    def test_user_creation(self, app):
        with app.app_context():
            user = User(
                username='dbtest',
                email='dbtest@test.com',
                role='viewer'
            )
            user.set_password('TestPass123!')
            db.session.add(user)
            db.session.commit()
            retrieved = User.query.filter_by(email='dbtest@test.com').first()
            assert retrieved is not None
