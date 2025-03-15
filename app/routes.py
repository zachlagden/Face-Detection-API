"""
Application routes

This module defines the API endpoints and request handling logic.
It contains route definitions for the face detection API.
"""

from flask import Blueprint, request, jsonify, send_file
import numpy as np
import cv2
import uuid
import time
import io
import json
from flask_limiter.util import get_remote_address

from app import limiter
from app.helpers.image_processor import process_image
from app.helpers.database import (
    save_job,
    get_job,
    get_result_image,
    get_recent_jobs,
    count_jobs,
)

# Create Blueprint
bp = Blueprint("routes", __name__)


@bp.route("/", methods=["GET"])
@limiter.exempt
def index():
    """
    Serve the index page with API documentation.

    Returns:
        HTML: Index HTML file
    """
    return send_file("templates/index.html")


@bp.route("/api/jobs", methods=["GET"])
@limiter.exempt
def get_jobs_api():
    """
    Retrieve a list of recent jobs.

    Query parameters:
        page (int): Page number (default: 1)
        limit (int): Number of jobs per page (default: 10)

    Returns:
        JSON: List of recent jobs with pagination metadata
    """
    try:
        # Get pagination parameters
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))

        # Get total job count
        total_jobs = count_jobs()

        # Get recent jobs
        jobs = get_recent_jobs(page, limit)

        # Calculate total pages
        total_pages = (total_jobs + limit - 1) // limit if limit > 0 else 1

        # Prepare response
        response = {
            "jobs": jobs,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_jobs": total_jobs,
                "total_pages": total_pages,
            },
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/overlay", methods=["POST"])
@limiter.limit("10 per minute", override_defaults=False)
def overlay():
    """
    Process an image to detect faces and overlay facial landmarks.

    This endpoint accepts an image file, processes it to detect faces and
    facial landmarks, and returns data about the detected features along with
    a URL to access the processed image.

    Returns:
        JSON: Job data including URLs and processing information
    """
    try:
        start_time = time.time()

        # Check if image file is present in the request
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]

        # Validate file type
        if not file.filename or "." not in file.filename:
            return jsonify({"error": "Invalid file"}), 400

        # Convert image file to numpy array
        image_np = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({"error": "Unable to decode image"}), 400

        # Process the image
        result_image, result_data = process_image(image)

        # Generate a unique job ID
        job_id = str(uuid.uuid4())

        # Convert the result image to bytes
        _, result_image_bytes = cv2.imencode(".png", result_image)

        # Calculate processing time
        end_time = time.time()
        processing_time = f"{(end_time - start_time) * 1000:.2f} ms"

        # Save job data to database
        job_data = save_job(
            job_id, result_image_bytes.tobytes(), processing_time, result_data
        )

        return jsonify(job_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/jobs/<job_id>", methods=["GET"])
@limiter.exempt
def get_job_route(job_id):
    """
    Retrieve information about a specific job.

    Args:
        job_id (str): Unique job identifier

    Returns:
        JSON: Job data including URLs and processing information
    """
    try:
        job_data = get_job(job_id)

        if job_data:
            return jsonify(job_data)
        else:
            return jsonify({"error": "Job not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/jobs/<job_id>/result_image.png", methods=["GET"])
@limiter.limit("20 per minute")
def get_result_image_route(job_id):
    """
    Retrieve the processed image for a specific job.

    Args:
        job_id (str): Unique job identifier

    Returns:
        File: Processed image as PNG
    """
    try:
        result_image = get_result_image(job_id)

        if result_image:
            return send_file(
                io.BytesIO(result_image),
                mimetype="image/png",
                as_attachment=True,
                download_name="result_image.png",
            )
        else:
            return jsonify({"error": "Image not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
