"""
Face Detection API - Entry point

This is the entry point for the Face Detection API application.
It initializes and runs the Flask application.
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
