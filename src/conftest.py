"""Pytest fixtures and configuration"""
import pytest
from io import BytesIO
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token

from .app_refactored import create_app
from .models import User, Document, Query, db
from .database import init_db, drop_db

@pytest.fixture(scope='session')
def app():
    """Create Flask app for testing"""
    app = create_app('testing')
    with app.app_context():
        init_db()
        yield app
        drop_db()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def admin_user(app):
    """Create admin test user"""
    with app.app_context():
        user = User(
            username='admin_test',
            email='admin@test.com',
            role='admin'
        )
        user.set_password('AdminPass123!')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def editor_user(app):
    """Create editor test user"""
    with app.app_context():
        user = User(
            username='editor_test',
            email='editor@test.com',
            role='editor'
        )
        user.set_password('EditorPass123!')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def viewer_user(app):
    """Create viewer test user"""
    with app.app_context():
        user = User(
            username='viewer_test',
            email='viewer@test.com',
            role='viewer'
        )
        user.set_password('ViewerPass123!')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def admin_token(admin_user, app):
    """Generate admin JWT token"""
    with app.app_context():
        return create_access_token(
            identity=admin_user.id,
            expires_delta=timedelta(hours=1)
        )

@pytest.fixture
def editor_token(editor_user, app):
    """Generate editor JWT token"""
    with app.app_context():
        return create_access_token(
            identity=editor_user.id,
            expires_delta=timedelta(hours=1)
        )

@pytest.fixture
def viewer_token(viewer_user, app):
    """Generate viewer JWT token"""
    with app.app_context():
        return create_access_token(
            identity=viewer_user.id,
            expires_delta=timedelta(hours=1)
        )

@pytest.fixture
def sample_document(admin_user, app):
    """Create sample document"""
    with app.app_context():
        doc = Document(
            user_id=admin_user.id,
            filename='test.pdf',
            content='Test content',
            file_type='pdf',
            size=1024,
            status='processed'
        )
        db.session.add(doc)
        db.session.commit()
        return doc

@pytest.fixture
def test_pdf_file():
    """Create test PDF file"""
    return (BytesIO(b'PDF test'), 'test.pdf')

@pytest.fixture(autouse=True)
def cleanup_db(app):
    """Cleanup after each test"""
    yield
    with app.app_context():
        db.session.query(Query).delete()
        db.session.query(Document).delete()
        db.session.query(User).delete()
        db.session.commit()
