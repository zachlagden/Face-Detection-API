"""
Application package initialization

This module initializes the Flask application and its extensions.
It creates the app factory and configures all necessary components.
"""

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv
import threading
import time

from app.helpers.database import init_db, cleanup_expired_jobs
from app.helpers.image_processor import init_face_detector
from config import Config

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1 per second", "10 per minute", "1000 per day"],
)


def create_app(config_class=Config):
    """
    Create and configure the Flask application.

    Args:
        config_class: Configuration class

    Returns:
        Flask: Configured Flask application
    """
    # Load environment variables
    load_dotenv()

    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize limiter
    limiter.init_app(app)
    limiter.key_func = lambda: get_remote_address()

    # Initialize database
    init_db(app)

    # Set up periodic cleanup task for expired jobs
    def run_cleanup():
        while True:
            cleanup_expired_jobs(app.config["JOB_EXPIRE_AFTER"])
            # Sleep for 15 minutes
            time.sleep(900)

    # Start cleanup thread
    cleanup_thread = threading.Thread(target=run_cleanup, daemon=True)
    cleanup_thread.start()

    # Initialize face detector
    predictor_path = app.config["PREDICTOR_PATH"]
    if os.path.exists(predictor_path):
        init_face_detector(predictor_path)
    else:
        app.logger.warning(
            f"Predictor file not found at {predictor_path}. "
            f"Face detection will not be available."
        )

    # Register routes
    from app.routes import bp as routes_bp

    app.register_blueprint(routes_bp)

    return app
