from flask import Flask, request, jsonify, send_file, render_template
import cv2
import dlib
import numpy as np
import time
import os
import uuid
import json

app = Flask(__name__)

# Load the face detector and shape predictor from Dlib
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("data/shape_predictor_68_face_landmarks.dat")

JOBS_FOLDER = "jobs"
if not os.path.exists(JOBS_FOLDER):
    os.makedirs(JOBS_FOLDER)


def process_image(image):
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
def index():
    return render_template("index.html")


@app.route("/overlay", methods=["POST"])
def overlay():
    try:
        start_time = time.time()

        # Get the image from the request
        file = request.files["image"]
        image_np = np.frombuffer(file.read(), np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        # Process the image
        result_image, result_data = process_image(image)

        # Generate a unique identifier for the job
        job_id = str(uuid.uuid4())
        job_folder = os.path.join(JOBS_FOLDER, job_id)
        os.makedirs(job_folder)

        # Save the processed image to the job folder
        result_image_path = os.path.join(job_folder, "result_image.png")
        cv2.imwrite(result_image_path, result_image)

        # Additional data about the request
        end_time = time.time()
        processing_time = end_time - start_time

        # Format the processing time in milliseconds
        processing_time = f"{processing_time * 1000:.2f} ms"

        # Create the data object to be saved as JSON and returned
        data = {
            "job_id": job_id,
            "result_image_url": f"/jobs/{job_id}/result_image.png",
            "processing_time": processing_time,
            "result_data": result_data,
        }

        with open(f"{job_folder}/job.json", "w+") as f:
            json.dump(data, f)

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id):
    try:
        # Find the job folder based on the job_id
        job_folder = os.path.join(JOBS_FOLDER, job_id)

        # Check if the job exists
        if not os.path.exists(job_folder):
            return jsonify({"error": "Job not found"}), 404

        # Load the job data
        with open(f"{job_folder}/job.json", "r") as f:
            data = json.load(f)

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/jobs/<job_id>/result_image.png", methods=["GET"])
def get_result_image(job_id):
    try:
        # Construct the absolute path to the result image
        result_image_path = os.path.join(
            os.getcwd(), JOBS_FOLDER, job_id, "result_image.png"
        )

        # Use send_file with the absolute path
        return send_file(
            result_image_path,
            mimetype="image/png",
            as_attachment=True,
            download_name="result_image.png",
        )
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
