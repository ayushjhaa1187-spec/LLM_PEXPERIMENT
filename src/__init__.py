"""
Main Application Package

This package initializes the Flask application using the factory pattern,
sets up the database, authentication, and registers all blueprints.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

from src.config import config
from src.utils.logger import app_logger

# Initialize extensions globally
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
cors = CORS()

def create_app():
    """
    Application factory function.
    
    Returns:
        Flask: The initialized Flask application instance.
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.database.url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.database.track_modifications
    app.config['SECRET_KEY'] = config.security.secret_key
    app.config['JWT_SECRET_KEY'] = config.security.jwt_secret_key
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": config.cors.origins}})
    
    # Setup logging
    app_logger.info(f"Initializing {config.app_name} v{config.app_version}")
    
    with app.app_context():
        # Register Blueprints
        from src.api.routes import api_bp
        from src.api.auth import auth_bp
        
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        
        # Initialize database (optional: use migrations in production)
        if config.is_development():
            db.create_all()
            app_logger.info("Database tables created (Development mode)")
            
    return app
