from flask import Flask, request, jsonify, send_file, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import cv2
import dlib
import numpy as np
import os
import uuid
import time
from pymongo import MongoClient
from gridfs import GridFS
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Create rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1 per second", "10 per minute", "1000 per day"],
    storage_uri=os.getenv("mongo_url"),
)

# Set the key function
limiter.key_func = lambda: request.remote_addr

# Connect to MongoDB and create TTL index for jobs collection
client = MongoClient(os.getenv("mongo_url"))
db = client[os.getenv("mongo_db")]

# Create TTL index for jobs collection with expiration after one hour
expire_after = int(os.getenv("mongo_job_expire_after"))

# Check if the TTL index exists and has the same expiration time
existing_index_info = db.jobs.index_information()
if (
    "created_at_1" not in existing_index_info
    or existing_index_info["created_at_1"]["expireAfterSeconds"] != expire_after
):
    # If the index doesn't exist or has a different expiration time, delete and recreate it
    if "created_at_1" in existing_index_info:
        db.jobs.drop_index("created_at_1")

    db.jobs.create_index("created_at", expireAfterSeconds=expire_after)

# Create GridFS object
fs = GridFS(db)

# Create face detector and facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("data/shape_predictor_68_face_landmarks.dat")


def process_image(image):
    """
    Process an image and return the processed image and data

    Args:
        image (numpy.ndarray): The image to process

    Returns:
        numpy.ndarray: The processed image
        list: The processed data
    """

    # Convert the image to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = detector(gray)

    result_data = []

    for face in faces:
        # Get facial landmarks
        landmarks = predictor(gray, face)

        # Draw a rectangle around the face
        cv2.rectangle(
            image,
            (face.left(), face.top()),
            (face.right(), face.bottom()),
            (255, 0, 0),
            2,
        )

        # Calculate the center of the head rectangle
        head_center_x = (face.left() + face.right()) // 2
        head_center_y = (face.top() + face.bottom()) // 2

        # Draw a dot at the center of the head
        cv2.circle(image, (head_center_x, head_center_y), 2, (255, 255, 255), -1)

        # Draw circles around each eye and find their centers
        left_eye_centers = [
            (landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)
        ]
        right_eye_centers = [
            (landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)
        ]

        # Calculate the center of each eye
        left_eye_center_x = sum([x for x, y in left_eye_centers]) // 6
        left_eye_center_y = sum([y for x, y in left_eye_centers]) // 6
        right_eye_center_x = sum([x for x, y in right_eye_centers]) // 6
        right_eye_center_y = sum([y for x, y in right_eye_centers]) // 6

        # Draw dots at the center of each eye
        cv2.circle(
            image, (left_eye_center_x, left_eye_center_y), 2, (255, 255, 255), -1
        )
        cv2.circle(
            image, (right_eye_center_x, right_eye_center_y), 2, (255, 255, 255), -1
        )

        # Draw a rectangle around the mouth
        mouth_left = (landmarks.part(48).x, landmarks.part(48).y)
        mouth_right = (landmarks.part(54).x, landmarks.part(54).y)
        cv2.rectangle(image, mouth_left, mouth_right, (0, 0, 255), 2)

        # Calculate the center of the mouth rectangle
        mouth_center_x = (mouth_left[0] + mouth_right[0]) // 2
        mouth_center_y = (mouth_left[1] + mouth_right[1]) // 2

        # Draw a dot at the center of the mouth
        cv2.circle(image, (mouth_center_x, mouth_center_y), 2, (255, 255, 255), -1)

        # Append data to result
        result_data.append(
            {
                "head_xy": (head_center_x, head_center_y),
                "mouth_xy": (mouth_center_x, mouth_center_y),
                "left_eye_xy": (left_eye_center_x, left_eye_center_y),
                "right_eye_xy": (right_eye_center_x, right_eye_center_y),
            }
        )

    return image, result_data


@app.route("/", methods=["GET"])
@limiter.exempt
def index():
    """Render the index.html template"""
    return render_template("index.html")


@app.route("/overlay", methods=["POST"])
@limiter.limit("10 per minute", override_defaults=False)
def overlay():
    """Process an image and return the processed image and data"""
    try:
        start_time = time.time()
        file = request.files["image"]
        image_np = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        result_image, result_data = process_image(image)

        job_id = str(uuid.uuid4())

        # Convert the result image to bytes
        _, result_image_bytes = cv2.imencode(".png", result_image)

        # Save the processed image to MongoDB GridFS
        result_image_id = fs.put(
            result_image_bytes.tobytes(), filename="result_image.png"
        )

        end_time = time.time()
        processing_time = end_time - start_time
        processing_time = f"{processing_time * 1000:.2f} ms"

        # Insert job data with timestamp
        db.jobs.insert_one(
            {
                "job_id": job_id,
                "result_image_url": f"/jobs/{job_id}/result_image.png",
                "result_image_id": result_image_id,
                "processing_time": processing_time,
                "result_data": result_data,
                "created_at": datetime.utcnow(),  # Add timestamp
            }
        )

        return jsonify(
            {
                "job_id": job_id,
                "result_image_url": f"/jobs/{job_id}/result_image.png",
                "processing_time": processing_time,
                "result_data": result_data,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/jobs/<job_id>", methods=["GET"])
@limiter.exempt
def get_job(job_id):
    """Get a job by its ID"""
    try:
        job_data = db.jobs.find_one({"job_id": job_id})
        del job_data["_id"]
        del job_data["result_image_id"]
        return jsonify(job_data)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/jobs/<job_id>/result_image.png", methods=["GET"])
@limiter.limit("20 per minute")
def get_result_image(job_id):
    """Get the result image of a job by its ID"""
    try:
        result_image_id = db.jobs.find_one({"job_id": job_id})["result_image_id"]
        result_image = fs.get(result_image_id).read()

        return send_file(
            io.BytesIO(result_image),
            mimetype="image/png",
            as_attachment=True,
            download_name="result_image.png",
        )
    except Exception as e:
        return jsonify({"error": str(e)})


# Run the app if this file is executed
if __name__ == "__main__":
    app.run(debug=True)
