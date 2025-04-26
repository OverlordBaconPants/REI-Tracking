"""
WSGI entry point for the REI-Tracker application.

This module provides the WSGI entry point for production servers like Gunicorn.
"""

from src.main import application as app

# This is the WSGI entry point
if __name__ == "__main__":
    app.run()
