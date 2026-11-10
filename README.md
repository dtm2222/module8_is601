# FastAPI Calculator — PostgreSQL & CI/CD

## Project Overview

This project is a web-based calculator built using Python and FastAPI. Throughout Modules 8, 9, and 10, I expanded the application by adding database functionality, user management, automated testing, Docker, and a CI/CD pipeline.

The goal of this project was to better understand how web applications work, how they connect to relational databases, and how automated testing and deployment can improve the development process.

## Features

- Web-based calculator using FastAPI
- Basic mathematical operations: addition, subtraction, multiplication, and division
- PostgreSQL database integration
- SQLAlchemy models for managing users
- Pydantic schemas for validating user information
- CRUD operations for interacting with the database
- Argon2 password hashing for securely storing passwords
- Automated unit, integration, and end-to-end testing
- Docker containerization
- GitHub Actions CI/CD pipeline
- Trivy security scanning
- Automated deployment to Docker Hub

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | Web application and API framework |
| PostgreSQL | Relational database |
| SQLAlchemy | Database models and interactions |
| Pydantic | Data validation |
| Argon2 | Password hashing |
| Docker | Application containerization |
| Docker Compose | Managing application services |
| pytest | Automated testing |
| Playwright | End-to-end testing |
| GitHub Actions | CI/CD automation |
| Trivy | Docker image security scanning |

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/dtm2222/module8_is601.git
cd module8_is601
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL

This project uses PostgreSQL for storing user information and calculator-related data.

Before running database functionality, configure the database connection using the environment variables expected by the application.

Do not commit database passwords or other credentials to GitHub.

### 5. Run the Application

```bash
uvicorn main:app --reload
```

Open the application at:

http://localhost:8000

FastAPI's interactive API documentation is available at:

http://localhost:8000/docs

## Database Implementation

For Module 10, I integrated SQLAlchemy with PostgreSQL to manage user information.

The User model includes:

- Username
- Email
- Password hash
- Account creation timestamp

I used Pydantic schemas to validate user data and implemented CRUD functions for database operations.

I also added Argon2 password hashing so user passwords are not stored as plain text.

## Testing

I used pytest and Playwright to verify the functionality of the application.

### Test Results

| Test Type | Results |
|---|---|
| Unit and integration tests | 35 passed |
| End-to-end tests | 3 passed |
| Unit/integration code coverage | 94% |

Run unit and integration tests:

```bash
python -m pytest tests/unit tests/integration -q
```

Run end-to-end tests:

```bash
python -m pytest tests/e2e -q
```

End-to-end tests require the web application to be running in the expected test environment.

## Docker

I used Docker to containerize the FastAPI application and Docker Compose to manage the application alongside PostgreSQL.

Build the Docker image locally:

```bash
docker build -t module10-fastapi-calculator .
```

Download the published image:

```bash
docker pull dtm2222/module10-fastapi-calculator:latest
```

The container requires the appropriate database configuration for PostgreSQL-dependent functionality.

## CI/CD Pipeline

For Module 10, I created a GitHub Actions workflow to automate testing, security checks, and deployment.

The pipeline performs the following steps:

1. Runs Python tests using a PostgreSQL test database.
2. Builds the Docker image.
3. Scans the image for HIGH and CRITICAL security vulnerabilities using Trivy.
4. Deploys the image to Docker Hub when the required checks pass.

The workflow uses GitHub repository secrets to securely authenticate with Docker Hub.

### CI/CD Results

All three workflow jobs completed successfully:

- Run Python Tests — Passed
- Docker Security Scan — Passed
- Deploy to Docker Hub — Passed

## Challenges and What I Learned

One of the biggest challenges I faced was getting all the different components to work together, especially PostgreSQL, Docker, and GitHub Actions.

I also ran into issues with Docker security vulnerabilities and compatibility problems after updating dependencies. By reviewing the errors, modifying the application, and rerunning my tests, I was able to resolve these problems.

This project helped me better understand how a web application is developed, tested, secured, and deployed.

## Project Links

**GitHub Repository:** https://github.com/dtm2222/module8_is601

**Docker Hub Repository:** https://hub.docker.com/r/dtm2222/module10-fastapi-calculator