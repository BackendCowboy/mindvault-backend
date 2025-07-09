# MindVault 🧠

**MindVault** is a personal growth tracker — built with FastAPI and SQLModel — that helps users journal daily, track moods, and reflect on their emotional patterns over time.

## Features

- ✅ User registration & login (JWT auth)
- ✅ Create, view, and manage journal entries
- ✅ Track moods with each entry
- ✅ 7-day summary route (journal & mood breakdown)
- ✅ Fully tested with Pytest
- ✅ Dockerized for deployment

## Tech Stack

- FastAPI + SQLModel + SQLite
- JWT authentication
- Pytest for test coverage
- Docker for containerization

## Getting Started

```bash
# Clone the repo
git clone https://github.com/BackendCowboy/mindvault-backend.git
cd mindvault-backend

# Create virtualenv & install deps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the app
uvicorn app.main:app --reload

# Run Tests 
bash 
pytest

# Docker
bash 
docker build -t mindvault .
docker run -d -p 8000:8000 mindvault

API Overview 
	•	POST /register: Create new user
	•	POST /login: Get JWT token
	•	POST /journals: Create new entry (auth required)
	•	GET /journals: List entries (auth required)
	•	GET /journals/7-day-summary: 7-day mood summary

Roadmap
	•	Add frontend (React or React Native)
	•	Smart AI-based journal feedback
	•	Daily mood reminders