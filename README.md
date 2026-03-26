# ECOIZ

ECOIZ is a team project with a user-facing app, admin web, backend, and database setup.

## Project Structure

- `admin-web/` - admin panel frontend built with Next.js
- `backend/` - main FastAPI backend with SQLAlchemy and Alembic
- `frontend/` - user-facing iOS/frontend application
- `database/` - legacy Prisma schema and seed data kept for reference

## Team Roles

- Akerke - backend
- Nurdana - AI
- Akon04 - database and admin web

## Tech Stack

- Next.js
- TypeScript
- React Query
- React Hook Form
- Zod
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Docker

## Run Backend

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
cp .env.example .env
docker compose up -d
pip install -e .
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Run Admin Web

```bash
cd admin-web
npm install
npm run dev
```

Open:

- `http://localhost:3000`

Live admin account:

- `admin@ecoiz.app / admin123`

## Notes

- `admin-web` currently supports both `mock` and `live` API modes.
- Current working runtime stack is `admin-web -> backend -> PostgreSQL`.
- `database/` is not the active runtime database layer right now because the backend uses SQLAlchemy + Alembic.
- If you run the real admin flow, start `backend` first, then `admin-web`.
