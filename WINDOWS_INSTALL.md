# Windows Installation Guide

This guide provides detailed steps for setting up the Face Detection API on Windows systems.

## Prerequisites

- Python 3.8 or higher
- Git

## Step 1: Install Required Build Tools

Dlib requires two key build tools to compile on Windows:

1. **Visual Studio Build Tools with C++ components**
   - Download from [Visual Studio Downloads](https://visualstudio.microsoft.com/downloads/)
   - Run the installer
   - Select "Desktop development with C++" workload
   - Complete the installation

2. **CMake**
   - Download from [CMake's official website](https://cmake.org/download/)
   - Run the installer and follow the prompts
   - Make sure to add CMake to your system PATH when prompted

## Step 2: Create and Activate Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
# Install dependencies without version constraints
pip install flask flask-limiter python-dotenv opencv-python dlib pytest
```

The key is to let pip choose compatible versions for your Python installation.

## Step 4: Download Shape Predictor Data File

1. Download the shape predictor file from [Dlib's official website](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)
2. Extract the file (you may need 7-Zip or a similar tool to extract .bz2 files)
3. Create a `data` folder in the project directory
4. Place the extracted `shape_predictor_68_face_landmarks.dat` file in the `data` folder

## Step 5: Set Up Environment Variables

Copy the `.env.example` file to `.env`:

```bash
copy .env.example .env
```

## Step 6: Run the Application

```bash
python main.py
```

## Troubleshooting

### Dlib Installation Issues

If you encounter errors installing dlib:

1. Make sure both Visual Studio Build Tools with C++ components and CMake are properly installed
2. Ensure you're using a compatible Python version
3. Verify that your environment variables are set correctly (PATH should include CMake)