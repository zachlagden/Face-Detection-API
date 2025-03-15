"""
Setup script for the Face Detection API

This script initializes the application directory structure
and SQLite database.
"""

import os
import argparse
import sqlite3
from pathlib import Path


def setup_directories():
    """Create the necessary directories for the application."""
    # Create data directory
    os.makedirs("data", exist_ok=True)

    # Create images directory
    os.makedirs("data/images", exist_ok=True)

    print("✅ Created directory structure")


def setup_database():
    """Initialize the SQLite database."""
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect("data/face_detection.db")
    cursor = conn.cursor()

    # Create jobs table
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS jobs (
        job_id TEXT PRIMARY KEY,
        result_image_path TEXT,
        processing_time TEXT,
        result_data TEXT,
        created_at INTEGER
    )
    """
    )

    # Create index on created_at for job expiration
    cursor.execute(
        """
    CREATE INDEX IF NOT EXISTS idx_created_at ON jobs(created_at)
    """
    )

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print("✅ Initialized SQLite database")


def create_env_file():
    """Create a default .env file if it doesn't exist."""
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(
                """# Database configuration
database_path=data/face_detection.db
job_expire_after=3600

# Storage
image_storage_path=data/images

# Application settings
debug=False
predictor_path=data/shape_predictor_68_face_landmarks.dat
"""
            )
        print("✅ Created .env file")
    else:
        print("⚠️ .env file already exists, skipping")


def check_predictor_file():
    """Check if the shape predictor file exists and provide instructions if it doesn't."""
    predictor_path = Path("data/shape_predictor_68_face_landmarks.dat")

    if predictor_path.exists():
        print("✅ Shape predictor file found")
    else:
        print("⚠️ Shape predictor file not found")
        print("Please download it from:")
        print("http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
        print("Extract it and place it in the data/ directory")


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Setup the Face Detection API")
    parser.add_argument(
        "--force", action="store_true", help="Force setup even if files exist"
    )
    args = parser.parse_args()

    print("Setting up Face Detection API...")

    # Setup directories
    setup_directories()

    # Setup database
    setup_database()

    # Create .env file
    create_env_file()

    # Check for predictor file
    check_predictor_file()

    print("\nSetup complete! 🎉")
    print("Run the application with: python main.py")


if __name__ == "__main__":
    main()
