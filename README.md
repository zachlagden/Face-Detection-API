# Face Detection API

The Face Detection API is a simple tool for detecting faces in images, overlaying facial landmarks, and providing additional data about the detected features.

## Features

- Face detection in uploaded images
- Facial landmark extraction
- Visual overlays for facial features
- API endpoints for image processing and result retrieval
- Job-based processing with results storage

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- Visual Studio Build Tools with C++ components (for dlib)
- CMake (for dlib)

> **Note for Windows users**: See [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) for detailed Windows-specific installation instructions.

### Installation Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/face-detection-api.git
   ```

2. Navigate to the project directory:

   ```bash
   cd face-detection-api
   ```

3. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

4. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

5. Download the shape predictor file:

   Download the shape predictor file from [Dlib's official website](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2), extract it, and place it in the `data/` folder.

6. Create a `.env` file:

   Copy the example environment file and modify as needed:

   ```bash
   cp .env.example .env
   ```

## Basic Usage

1. Run the Flask application:

   ```bash
   python main.py
   ```

   The API will be accessible at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

2. Use the API to detect faces in an image:

   - **Endpoint:** `POST /overlay`
   - **Request Type:** Multipart/form-data
   - **Request Parameter:**
     - `image`: Upload an image file.

   **Example using cURL:**

   ```bash
   curl -X POST -H "Content-Type: multipart/form-data" -F "image=@/path/to/your/image.jpg" http://127.0.0.1:5000/overlay
   ```

   The response will include a unique job ID, a URL to the processed image, processing time, and data about the detected faces.

3. Retrieve information about a specific job:

   - **Endpoint:** `GET /jobs/<job_id>`
   - **Replace `<job_id>` with the actual job ID obtained from the overlay response.

   **Example using cURL:**

   ```bash
   curl http://127.0.0.1:5000/jobs/unique_job_id
   ```

   This will provide details about the specified job.

4. Retrieve the processed image associated with a job:

   - **Endpoint:** `GET /jobs/<job_id>/result_image.png`
   - **Replace `<job_id>` with the actual job ID obtained from the overlay response.

   **Example using cURL:**

   ```bash
   curl -OJ http://127.0.0.1:5000/jobs/unique_job_id/result_image.png
   ```

   This will download the processed image.

## Project Structure

- `app/`: Main application package
  - `helpers/`: Helper modules and functions
    - `database.py`: Database operations (SQLite)
    - `image_processor.py`: Face detection and image processing
  - `templates/`: HTML templates
    - `index.html`: API documentation page
- `data/`: Shape predictor data file and SQLite database
  - `images/`: Storage for processed images
- `tests/`: Test suite
  - `test_image_processor.py`: Tests for image processing
  - `test_routes.py`: Tests for API endpoints
- `main.py`: Application entry point
- `config.py`: Configuration settings
- `.env.example`: Example environment variables

## Running Tests

This project includes a test suite using pytest. To run the tests:

```bash
pytest
```

## Rate Limiting

The API implements rate limiting to prevent abuse:
- 1 request per second (default)
- 10 requests per minute (default)
- 1000 requests per day (default)

These limits can be configured in the application.

## Data Storage

- SQLite database for storing job information
- Local file system for storing processed images
- Automatic cleanup of expired jobs and images