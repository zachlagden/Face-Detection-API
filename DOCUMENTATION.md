# Face Detection API Documentation

## Introduction

Welcome to the Face Detection API documentation. This API is designed to detect faces in images, extract facial landmarks, and provide additional information about the detected features.

## Table of Contents

1. [Endpoints](#endpoints)
   - [Overlay](#overlay)
   - [Get Job](#get-job)
   - [Get Result Image](#get-result-image)
2. [Request and Response Formats](#request-and-response-formats)
   - [Overlay Endpoint](#overlay-endpoint)
   - [Get Job Endpoint](#get-job-endpoint)
   - [Get Result Image Endpoint](#get-result-image-endpoint)

## Endpoints

### Overlay

#### `POST /overlay`

This endpoint processes an image to detect faces, overlay facial landmarks, and provide additional data.

**Request Parameters:**

- `image`: A file parameter containing the image to be processed.

**Response:**

```json
{
    "job_id": "unique_job_id",
    "result_image_url": "/jobs/unique_job_id/result_image.png",
    "processing_time": "42.56 ms",
    "result_data": [
        {
            "head_xy": (x, y),
            "mouth_xy": (x, y),
            "left_eye_xy": (x, y),
            "right_eye_xy": (x, y)
        },
        // Additional entries for multiple faces if present
    ]
}
```

### Get Job

#### `GET /jobs/<job_id>`

This endpoint retrieves information about a specific job based on its unique identifier.

**Response:**

```json
{
    "job_id": "unique_job_id",
    "result_image_url": "/jobs/unique_job_id/result_image.png",
    "processing_time": "42.56 ms",
    "result_data": [
        {
            "head_xy": (x, y),
            "mouth_xy": (x, y),
            "left_eye_xy": (x, y),
            "right_eye_xy": (x, y)
        },
        // Additional entries for multiple faces if present
    ]
}
```

### Get Result Image

#### `GET /jobs/<job_id>/result_image.png`

This endpoint retrieves the processed image associated with a specific job.

## Request and Response Formats

### Overlay Endpoint

#### Request Format:

```http
POST /overlay
Content-Type: multipart/form-data

<image file>
```

#### Response Format:

```json
{
    "job_id": "unique_job_id",
    "result_image_url": "/jobs/unique_job_id/result_image.png",
    "processing_time": "42.56 ms",
    "result_data": [
        {
            "head_xy": (x, y),
            "mouth_xy": (x, y),
            "left_eye_xy": (x, y),
            "right_eye_xy": (x, y)
        },
        // Additional entries for multiple faces if present
    ]
}
```

### Get Job Endpoint

#### Response Format:

```json
{
    "job_id": "unique_job_id",
    "result_image_url": "/jobs/unique_job_id/result_image.png",
    "processing_time": "42.56 ms",
    "result_data": [
        {
            "head_xy": (x, y),
            "mouth_xy": (x, y),
            "left_eye_xy": (x, y),
            "right_eye_xy": (x, y)
        },
        // Additional entries for multiple faces if present
    ]
}
```

### Get Result Image Endpoint

#### Response Format:

The response is the processed image in PNG format.

## Conclusion

Thank you for using the Face Detection API. If you have any questions or encounter issues, please contact support at [contact@whsmith.me](mailto:contact@whsmith.me?subject=Face%20Detection%20API%20Support).
