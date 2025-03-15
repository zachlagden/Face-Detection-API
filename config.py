"""
Configuration module for the Face Detection API

This module defines configuration settings for the application.
It uses environment variables for configuration with sensible defaults.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration settings for the application."""

    # Database settings
    DATABASE_PATH = os.getenv("database_path", "data/face_detection.db")
    JOB_EXPIRE_AFTER = int(
        os.getenv("job_expire_after", 3600)
    )  # Default 1 hour in seconds

    # Application settings
    PREDICTOR_PATH = os.getenv(
        "predictor_path", "data/shape_predictor_68_face_landmarks.dat"
    )
    DEBUG = os.getenv("debug", "False").lower() == "true"
    IMAGE_STORAGE_PATH = os.getenv("image_storage_path", "data/images")
