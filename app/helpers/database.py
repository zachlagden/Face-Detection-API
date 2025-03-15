"""
Database helper module

This module handles database operations for the Face Detection API.
It provides functions for SQLite database operations and file storage.
"""

import sqlite3
import os
import json
import time
from datetime import datetime
import shutil

# Global variables
db_connection = None
image_storage_path = None


def init_db(app):
    """
    Initialize the database connection and setup tables.

    Args:
        app: Flask application instance
    """
    global db_connection, image_storage_path

    # Set image storage path
    image_storage_path = app.config["IMAGE_STORAGE_PATH"]

    # Create image storage directory if it doesn't exist
    if not os.path.exists(image_storage_path):
        os.makedirs(image_storage_path)

    # Get database path from config
    db_path = app.config["DATABASE_PATH"]

    # Create directory for database if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    # Connect to SQLite database
    db_connection = sqlite3.connect(db_path, check_same_thread=False)
    db_connection.row_factory = sqlite3.Row  # Allow accessing columns by name

    # Create a cursor for initialization
    cursor = db_connection.cursor()

    # Create jobs table if it doesn't exist
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

    # Commit changes and close cursor
    db_connection.commit()
    cursor.close()

    # Schedule cleanup task
    cleanup_expired_jobs(app.config["JOB_EXPIRE_AFTER"])


def cleanup_expired_jobs(expire_after):
    """
    Clean up expired jobs and their associated files.

    Args:
        expire_after (int): Time in seconds after which jobs expire
    """
    try:
        # Calculate expiration timestamp
        expiration_time = int(time.time()) - expire_after

        # Create a new cursor for this operation
        cursor = db_connection.cursor()

        # Get expired jobs
        cursor.execute(
            "SELECT job_id, result_image_path FROM jobs WHERE created_at < ?",
            (expiration_time,),
        )
        expired_jobs = cursor.fetchall()

        # Delete files associated with expired jobs
        for job in expired_jobs:
            if job["result_image_path"] and os.path.exists(job["result_image_path"]):
                try:
                    os.remove(job["result_image_path"])
                except OSError as e:
                    print(f"Error deleting image file: {e}")

        # Delete expired jobs from database
        cursor.execute("DELETE FROM jobs WHERE created_at < ?", (expiration_time,))
        db_connection.commit()

        # Close cursor
        cursor.close()
    except Exception as e:
        print(f"Error in cleanup_expired_jobs: {e}")


def save_job(job_id, result_image_bytes, processing_time, result_data):
    """
    Save job data and processed image to the database and file system.

    Args:
        job_id (str): Unique job identifier
        result_image_bytes (bytes): Processed image data
        processing_time (str): Processing time in milliseconds
        result_data (list): Data about detected faces

    Returns:
        dict: Job data including URLs and processing information
    """
    try:
        # Create a new cursor for this operation
        cursor = db_connection.cursor()

        # Create job directory
        job_dir = os.path.join(image_storage_path, job_id)
        if not os.path.exists(job_dir):
            os.makedirs(job_dir)

        # Save image to file
        image_path = os.path.join(job_dir, "result_image.png")
        with open(image_path, "wb") as f:
            f.write(result_image_bytes)

        # Create job data
        job_data = {
            "job_id": job_id,
            "result_image_url": f"/jobs/{job_id}/result_image.png",
            "processing_time": processing_time,
            "result_data": result_data,
        }

        # Insert job data into database
        cursor.execute(
            "INSERT INTO jobs (job_id, result_image_path, processing_time, result_data, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                job_id,
                image_path,
                processing_time,
                json.dumps(result_data),
                int(time.time()),
            ),
        )
        db_connection.commit()

        # Close cursor
        cursor.close()

        return job_data
    except Exception as e:
        print(f"Error in save_job: {e}")
        raise


def get_job(job_id):
    """
    Retrieve job data from the database.

    Args:
        job_id (str): Unique job identifier

    Returns:
        dict: Job data or None if not found
    """
    try:
        # Create a new cursor for this operation
        cursor = db_connection.cursor()

        cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        job_data = cursor.fetchone()

        # Close cursor
        cursor.close()

        if job_data:
            try:
                result_data = json.loads(job_data["result_data"])
            except (json.JSONDecodeError, TypeError):
                result_data = []

            response_data = {
                "job_id": job_data["job_id"],
                "result_image_url": f"/jobs/{job_data['job_id']}/result_image.png",
                "processing_time": job_data["processing_time"],
                "result_data": result_data,
                "created_at": job_data["created_at"],
            }
            return response_data

        return None
    except Exception as e:
        print(f"Error in get_job: {e}")
        return None


def get_result_image(job_id):
    """
    Retrieve the processed image for a job.

    Args:
        job_id (str): Unique job identifier

    Returns:
        bytes: Image data or None if not found
    """
    try:
        # Create a new cursor for this operation
        cursor = db_connection.cursor()

        cursor.execute("SELECT result_image_path FROM jobs WHERE job_id = ?", (job_id,))
        job = cursor.fetchone()

        # Close cursor
        cursor.close()

        if (
            job
            and job["result_image_path"]
            and os.path.exists(job["result_image_path"])
        ):
            with open(job["result_image_path"], "rb") as f:
                return f.read()

        return None
    except Exception as e:
        print(f"Error in get_result_image: {e}")
        return None


def get_recent_jobs(page=1, limit=10):
    """
    Retrieve a list of recent jobs with pagination.

    Args:
        page (int): Page number (starting from 1)
        limit (int): Number of jobs per page

    Returns:
        list: List of job data
    """
    try:
        # Create a new cursor for this operation
        cursor = db_connection.cursor()

        # Validate inputs
        page = max(1, int(page))
        limit = max(1, int(limit))

        # Calculate offset
        offset = (page - 1) * limit

        # Query database for recent jobs
        cursor.execute(
            "SELECT job_id, processing_time, result_data, created_at FROM jobs ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        jobs = cursor.fetchall()

        # Close cursor
        cursor.close()

        # Convert to list of dictionaries
        result = []
        for job in jobs:
            try:
                result_data = json.loads(job["result_data"])
                face_count = len(result_data)
            except (json.JSONDecodeError, TypeError):
                result_data = []
                face_count = 0

            result.append(
                {
                    "job_id": job["job_id"],
                    "result_image_url": f"/jobs/{job['job_id']}/result_image.png",
                    "processing_time": job["processing_time"],
                    "face_count": face_count,
                    "created_at": job["created_at"],
                }
            )

        return result
    except Exception as e:
        print(f"Error in get_recent_jobs: {e}")
        return []


def count_jobs():
    """
    Count the total number of jobs in the database.

    Returns:
        int: Total number of jobs
    """
    try:
        # Create a new cursor for this operation
        cursor = db_connection.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM jobs")
        result = cursor.fetchone()

        # Close cursor
        cursor.close()

        return result["count"] if result else 0
    except Exception as e:
        print(f"Error in count_jobs: {e}")
        return 0
