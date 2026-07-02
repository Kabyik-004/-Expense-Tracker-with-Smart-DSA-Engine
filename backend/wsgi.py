"""
WSGI entry point for production servers (Gunicorn, uWSGI, etc.).
Run with: gunicorn wsgi:app
"""

import os
from app import create_app
from app.config import config_by_name

env = os.getenv("FLASK_ENV", "production")
app = create_app(config_by_name.get(env, config_by_name["production"]))
