# Face Detection API

The Face Detection API is a simple tool for detecting faces in images, overlaying facial landmarks, and providing additional data about the detected features.

## Installation and Setup

### Prerequisites

- Python 3.6 or higher
- Pip (Python package installer)
- Visual Studio Build Tools (required for dlib)

### Installation Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/thewhsmith/Face-Detection-API.git
   ```

2. Navigate to the project directory:

   ```bash
   cd Face-Detection-API
   ```

3. Install Visual Studio Build Tools from [Visual Studio Downloads](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

4. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

5. Download the shape predictor file from [Dlib's official website](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2) and place it in the `data/` folder.

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
   - \*\*Replace `<job_id>` with the actual job ID obtained from the overlay response.

   **Example using cURL:**

   ```bash
   curl http://127.0.0.1:5000/jobs/unique_job_id
   ```

   This will provide details about the specified job.

4. Retrieve the processed image associated with a job:

   - **Endpoint:** `GET /jobs/<job_id>/result_image.png`
   - \*\*Replace `<job_id>` with the actual job ID obtained from the overlay response.

   **Example using cURL:**

   ```bash
   curl -OJ http://127.0.0.1:5000/jobs/unique_job_id/result_image.png
   ```

   This will download the processed image.

## Conclusion

Enjoy using the Face Detection API! If you have any questions or encounter issues, feel free to reach out to support at [zach@zachlagden.uk](mailto:zach@zachlagden.uk?subject=Face%20Detection%20API%20Support).
