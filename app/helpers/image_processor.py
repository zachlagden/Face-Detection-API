"""
Image processing module

This module handles face detection and facial landmark extraction.
It provides functions for processing images and extracting facial features.
"""

import cv2
import dlib
import numpy as np
import os

# Initialize face detector and facial landmark predictor
detector = None
predictor = None


def init_face_detector(predictor_path):
    """
    Initialize the face detector and facial landmark predictor.

    Args:
        predictor_path (str): Path to the shape predictor file
    """
    global detector, predictor

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(predictor_path)


def process_image(image):
    """
    Process an image to detect faces and extract facial landmarks.

    This function detects faces in the input image, extracts facial landmarks,
    and adds visual markers for key facial features. It returns the processed
    image and data about the detected features.

    Args:
        image (numpy.ndarray): The image to process

    Returns:
        tuple: A tuple containing:
            - numpy.ndarray: The processed image with facial landmarks
            - list: Data about the detected facial features
    """
    if detector is None or predictor is None:
        raise RuntimeError(
            "Face detector not initialized. Call init_face_detector first."
        )

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
