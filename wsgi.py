"""WSGI Application Entry Point
Imports the Flask application from src.app_refactored
"""
from src.app_refactored import app

if __name__ == "__main__":
    app.run()
