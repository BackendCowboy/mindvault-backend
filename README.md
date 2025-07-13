# 🧠 MindVault — AI-Powered Journal Tracker

MindVault is a backend API that lets users log journal entries, analyze mood trends, and receive AI-generated reflections via OpenAI.

---
Markdown:
# 🧠 MindVault — AI-Powered Journal Tracker

MindVault is a backend API for journaling with AI-powered reflections. It helps users log thoughts, analyze mood trends, and track mental wellness. Built for developers who care about clarity, growth, and clean backend logic.

---

## 🚀 Features

- 🔐 **JWT Authentication** (Register/Login)
- 📓 **CRUD Journal Entries**
- 🤖 **OpenAI GPT**-Generated Reflections
- 📊 **Mood Tracking**, **7-Day Summaries**, **Stats**, and **Streaks**
- 🔎 Filter by **mood**, **search**, and **date**
- 🧱 Rate limiting with `slowapi`
- 🐳 **Dockerized**: FastAPI + PostgreSQL + pgAdmin
- 🔄 **Alembic Migrations**
- ✅ **Pytest** suite for auth and journals

---

## 🧱 Tech Stack

- **Python 3.11**
- **FastAPI** + **SQLModel**
- **PostgreSQL** (via Docker)
- **Alembic** for migrations
- **OpenAI GPT-3.5+** (for reflections)
- **Docker + Docker Compose**
- **Pytest** for testing

---

## 📦 Installation

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/mindvault-backend.git
cd mindvault-backend

2. Create .env file

Create a .env file at the root with the following:
env
OPENAI_API_KEY=your-openai-api-key
SECRET_KEY=your-super-secret-key
DATABASE_URL=postgresql://postgres:password@localhost:5432/mindvault

3. Create virtual environment & install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

4. Run Alembic migrations
```bash
alembic upgrade head

5. Start the app
```bash
uvicorn app.main:app --reload
App will be available at: http://127.0.0.1:8000

🐳 Running with Docker

1. Start PostgreSQL + pgAdmin + API
```bash
docker-compose up --build
This will:
	•	Launch PostgreSQL container (mindvault-db)
	•	Launch pgAdmin for DB visualization (at port 5050)
	•	Run your FastAPI backend

2. Apply Alembic migrations inside the container
```bash 
docker-compose exec mindvault-api alembic upgrade head


🧪 Running Tests
```bash 
pytest 

🧠 Example: Create Journal Entry (with GPT reflection)
```bash
curl -X POST http://127.0.0.1:8000/journals \
-H "Authorization: Bearer <your_token>" \
-H "Content-Type: application/json" \
-d '{
  "title": "A Calm Morning",
  "content": "Woke up and felt grounded. Went for a walk and did breathwork.",
  "mood": "peaceful"
}'

📁 Project Structure
mindvault-backend/
│
├── app/
│   ├── ai/                   # OpenAI utils
│   ├── routes/               # Route modules
│   ├── schemas/              # Pydantic schemas
│   ├── models.py             # SQLModel models
│   ├── auth.py               # JWT + auth
│   ├── database.py           # DB engine
│   ├── limiter.py            # Rate limiter
│   ├── config.py             # Env config
│   └── main.py               # FastAPI app entrypoint
│
├── alembic/                  # Migrations
│   └── versions/             # Versioned migration files
│
├── tests/                    # Pytest test suite
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
└── .env                      # Your secrets (not committed)

🔐 Authentication
	•	Register: POST /auth/register
	•	Login: POST /auth/login → returns access_token
	•	Use Authorization: Bearer <token> header for protected routes

⸻

🧠 AI Reflections

Journals use OpenAI to generate self-reflective content using your entry’s title, mood, and body. Ensure your OPENAI_API_KEY is valid and you have credits.

⸻

🛠 Dev Notes
	•	Run alembic revision --autogenerate -m "your message" to generate migrations
	•	Use .env to store sensitive credentials
	•	Use reset_db.sh (optional) to nuke and reset the DB locally

⸻

❤️ Built With Purpose

MindVault was crafted to help you reflect, grow, and track your mental clarity — one journal entry at a time.

