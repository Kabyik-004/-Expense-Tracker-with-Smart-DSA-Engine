"""
Application entry point.
Run with: python run.py
"""

import os

from app import create_app
from app.config import config_by_name

env = os.getenv("FLASK_ENV", "development")
app = create_app(config_by_name.get(env, config_by_name["development"]))

if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=app.config.get("DEBUG", False),
    )
