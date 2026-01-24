"""
Flask Application Wrapper

This file provides a compatibility layer for existing tools that expect
an 'app.py' file at the root or src directory.
"""

from src.main import app

if __name__ == "__main__":
    app.run()
