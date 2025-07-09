# 🧠 MindVault – Personal Growth Tracker API

MindVault is a FastAPI-powered backend for a personal growth app. It includes features like mood tracking, journal entry logging, and secure user authentication — all built for introspection, healing, and progress.

---

## 🚀 Tech Stack

- **Python 3.13**
- **FastAPI**
- **SQLModel**
- **SQLite** (dev) → PostgreSQL (prod-ready)
- **JWT Authentication**
- **Pytest** for automated route testing

---

## 📦 Features

- 🔐 **User Auth** (Register, Login, JWT Tokens)
- 📓 **Journal Entries** (Create, View, Filter)
- 🎭 **Mood Tracking** (Tag entries by emotion)
- 🧪 **Full Test Coverage** for user flow

---

## 🧪 Run the Tests

```bash
pytest

🛠️ Coming Soon
	•	🐳 Docker support
	•	🧪 GitHub Actions CI
	•	🌐 GraphQL integration
	•	🧠 Smart mood insights (AI-enhanced)
	•	📱 React Native frontend

📁 Project Structure
mindvault-backend/
├── app/
│   ├── init.py
│   ├── auth.py              # Authentication logic (JWT, password hashing)
│   ├── config.py            # App settings (e.g. secret key, token expiry)
│   ├── database.py          # DB engine and session
│   ├── main.py              # FastAPI entry point
│   ├── models.py            # SQLModel models
│   └── routes.py            # API endpoints (register, login, journals)
│
├── tests/
│   ├── init.py
│   ├── conftest.py          # Test fixtures and test DB session
│   └── test_routes.py       # End-to-end user flow test
│
├── journal.db               # SQLite DB (generated)
├── README.md                # Project overview and usage
├── requirements.txt         # Dependencies
└── .gitignore               # Ignored files

🧑‍💻 About the Developer

Built by Aliou — aka the BackendCowboy. Focused on clean architecture, deep learning, and digital healing tools.

## 🚀 Run with Docker

To build and run the app in a Docker container:

```bash
docker build -t mindvault .
docker run -d -p 8000:8000 mindvault