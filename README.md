Videoflix Backend
Videoflix Backend is the server-side component of a video streaming application inspired by Netflix. It is built using Django and Django REST Framework (DRF), with support for user authentication (registration, login, activation, logout, token refresh, password reset), video content management, and HLS (HTTP Live Streaming) video transcoding for multiple resolutions. The backend uses PostgreSQL as the database, Redis for caching and RQ (Redis Queue) for background tasks, and is fully containerized with Docker for easy setup and deployment.
Key features:

User authentication with JWT tokens stored in HttpOnly cookies.
Video upload via admin panel, with automatic HLS transcoding (480p, 720p, 1080p) using FFmpeg in background tasks.
API endpoints for video list, HLS manifest, and segments, with JWT authentication.
Caching for video list using Redis.

This README provides a step-by-step guide to set up and run the backend locally using Docker. The project is designed for development mode but can be extended for production.
Requirements
To run the backend, you need:

Docker (version 20.10+ recommended) and Docker Compose (version 1.29+ or Docker Compose v2+).
Git (to clone the repository).
A code editor (e.g., VS Code) for optional modifications.
No additional local installations are required, as everything is containerized.

The backend runs on port 8000 by default (exposed from the "web" container). Ensure this port is free on your machine.
Step-by-Step Setup and Running Instructions
Follow these steps in order to set up and run the Videoflix backend. All commands should be run in your terminal from the project root directory (where the docker-compose.yml file is located).


Step 1 
Clone the Repository
Clone the GitHub repository to your local machine:

git clone <your-repo-url>  # Replace with your GitHub repo URL
cd <projectfolder>

- Detail: This downloads the code base, including Dockerfile, docker-compose.yml, requirements.txt, and app files. If you have a private repo, use your credentials or SSH.


Step 2
Set up a virtual environment:

python -m venv env
env/Scripts/activate  # Windows
source env/bin/activate  # macOS/Linux

*Note: On macOS/Linux, python3 may have to be used instead of python.


Step 3
Install the required packages: 
The requirements.txt file contains all necessary Python packages.

pip install -r requirements.txt

Note: If a requirements.txt file is not present, you can generate one from the existing project setup using pip freeze > requirements.txt.


Step 4
Create Environment Variables:
Create a .env file in the project's root directory by copying env.example:

cp .env.template .env

Or by creating a new file with the following content. The default values are generally fine for local development.

# Django
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database
DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=supersecretpassword

# Django Superuser (will be created automatically on startup)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=adminpassword


Step 5
Build and Start Docker Containers:
This command builds the images, starts all services (web API, database, Redis, RQ worker), and runs the database migrations.

# just for Mac user
chmod +x backend.entrypoint.sh

# for all systems
docker-compose up --build

You can add -d to run the containers in the background.


Step 6
The Project is now ready to go!
You can access the application now at http://127.0.0.1:8000.