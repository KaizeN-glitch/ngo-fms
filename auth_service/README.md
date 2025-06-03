# Auth Service

This is an authentication microservice built with FastAPI, SQLAlchemy, and PostgreSQL. It provides user registration and authentication endpoints, and is designed to run as part of a Dockerized microservices architecture.

## Prerequisites

- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your system.

## Running the Project

1. **Clone the repository** (if you haven't already):
   ```powershell
   git clone <your-repo-url>
   cd "FMS Project development"
   ```

2. **Start the services using Docker Compose:**
   ```powershell
   docker-compose up --build
   ```
   This will build and start both the PostgreSQL database and the `auth_service` FastAPI app.

3. **Access the Auth Service API:**
   - The API will be available at: [http://localhost:8001](http://localhost:8001)
   - Interactive API docs (Swagger UI): [http://localhost:8001/docs](http://localhost:8001/docs)

4. **Stopping the services:**
   ```powershell
   docker-compose down
   ```

## Running the Project with Uvicorn (Without Docker)

You can also run the Auth Service directly using Uvicorn:

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
2. **Set environment variables:**
   You must set `DATABASE_URL` and `AUTH_SECRET_KEY` before running the server. For example:
   ```powershell
   $env:DATABASE_URL = "postgresql://postgresql://fms_user:12345@localhost:5432/fms_db
   $env:AUTH_SECRET_KEY = "CHANGE_THIS_SECRET"
   ```
   Adjust the values as needed for your environment.

3. **Start the FastAPI server:**
   ```powershell
   uvicorn main:app --reload --host 0.0.0.0 --port 8001
   ```

The API will be available at [http://localhost:8001](http://localhost:8001) and the docs at [http://localhost:8001/docs](http://localhost:8001/docs).

## Environment Variables

- `DATABASE_URL`: Connection string for the PostgreSQL database (set in `docker-compose.yml`).
- `AUTH_SECRET_KEY`: Secret key for JWT token generation (set in `docker-compose.yml`).

## Project Structure

- `main.py` - FastAPI app entry point
- `models.py` - SQLAlchemy models
- `crud.py` - Database operations
- `schemas.py` - Pydantic schemas
- `database.py` - Database connection setup
- `dependencies.py` - Dependency injection for FastAPI
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container build instructions
- `tests/` - Unit tests

## Running Tests

1. **Install dependencies locally (optional, for running tests outside Docker):**
   ```powershell
   pip install -r requirements.txt
   ```
2. **Run tests:**
   ```powershell
   pytest tests/
   ```

---

For more details, see the code and comments in each file.
