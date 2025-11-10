# AgriSense Backend (FastAPI)

This folder contains a minimal FastAPI backend implementing JWT authentication (signup, login, me) using SQLAlchemy and SQLite by default.

Quick start (Windows PowerShell):

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate; pip install -r backend/requirements.txt
```

2. Copy `.env.example` to `.env` and update `SECRET_KEY` if needed.

3. Run the app:

```powershell
uvicorn app.main:app --reload --port 8000 --root-path ""
```

The API will be available at `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/docs` for interactive Swagger UI.

Files created:
- `app/main.py` — application factory, CORS, router registration
- `app/database.py` — SQLAlchemy engine, session, Base
- `app/models.py` — SQLAlchemy ORM models
- `app/schemas.py` — Pydantic request/response models
- `app/crud.py` — DB helper functions for users
- `app/auth.py` — /api/auth router (signup, login, me) + JWT helpers
- `.env.example` — sample environment variables

Notes:
- Default DB is SQLite (file `agrisense_dev.db`). You can change `DATABASE_URL` in `.env` to a PostgreSQL connection string later.
- Do NOT modify frontend. The endpoints accept JSON and return JSON suitable for your React forms.
