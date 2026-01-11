
# Simple Social — Full-Stack Media Platform

A modern, full-stack social media application built with a FastAPI backend and a Streamlit frontend. It features secure JWT authentication, cloud-based media uploads (images and videos), and a real-time interactive feed.

## Features

- Secure authentication with user registration and login using JWT via fastapi-users
- Upload images and videos with cloud storage using Cloudinary
- Shared social feed showing posts from all users with captions
- Users can delete their own posts from the feed
- Async backend built with FastAPI and SQLAlchemy
- Simple interactive frontend built with Streamlit

## Technology Stack

Backend API: FastAPI, Uvicorn  
Authentication: FastAPI-Users, JWT  
Database & ORM: SQLAlchemy (Async), SQLite  
File Storage: Cloudinary API  
Frontend: Streamlit  
Validation: Pydantic  
Environment Config: python-dotenv  
Package Manager: uv or pip

## Installation and Setup

### Prerequisites

- Python 3.10 or higher (3.13 tested)
- Git
- Cloudinary account (free tier works)
- Package manager: uv (recommended) or pip

### Clone Repository
```bash
git clone https://github.com/Rohit025005/Postly.git
cd Postly
```

### Install Dependencies (Using uv)
```bash
pip install uv
uv venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
uv sync
```

### Install Dependencies (Using pip)
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
pip install -e .
```

### Environment Variables

Create a `.env` file in the project root:
```env
CLOUDINARY_CLOUD_NAME=your_cloud_name_here
CLOUDINARY_API_KEY=your_api_key_here
CLOUDINARY_API_SECRET=your_api_secret_here
```

Do not commit this file to version control.

### Run Backend
```bash
python main.py

```
or
```bash
uv run main.py
```

API runs at: http://localhost:8000  
Docs: http://localhost:8000/docs

### Run Frontend

Open another terminal:
```bash
streamlit run frontend.py
```
or
```bash
uv run streamlit run frontend.py
```

App runs at: http://localhost:8501

## Usage

1. Open http://localhost:8501 in browser
2. Sign up with email and password
3. Log in using same credentials
4. Use sidebar navigation:
   - Feed: view all posts and delete your own
   - Upload: upload image or video with caption

## API Endpoints

- `POST /auth/register` — Register user
- `POST /auth/jwt/login` — Login and receive JWT
- `GET /auth/me` — Get current user profile (auth required)
- `POST /upload` — Upload image or video (auth required)
- `GET /feed` — Get all posts (auth required)
- `DELETE /posts/{post_id}` — Delete own post (auth required)

## Project Structure
```
.
├── frontend.py
├── main.py
├── pyproject.toml
├── .env.example
├── app/
│   ├── app.py
│   ├── db.py
│   ├── schemas.py
│   ├── users.py
│   └── images.py
└── .venv/
```

## Developer

Rohit Sarwadikar  
GitHub: https://github.com/Rohit025005  
LinkedIn: https://linkedin.com/in/RohitSarwadikar

Check API docs at http://localhost:8000/docs for reference