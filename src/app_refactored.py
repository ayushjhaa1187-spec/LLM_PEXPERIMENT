"""
Refactored Application Entry Point

This module provides a professionally structured version of the main application,
utilizing the factory pattern, centralized configuration, and robust logging.

Author: LLM Government Consulting Team
Date: January 24, 2026
"""

from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from src.config import config
from src.utils.logger import app_logger
from src.llm_engine import MultiAgentRAGSystem

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    return app

app = create_app()

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Routes
@app.route('/api/health')
def health():
    app_logger.info("Health check requested")
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host=config.host, port=config.port, debug=config.debug)
