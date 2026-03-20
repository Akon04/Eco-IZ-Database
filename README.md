# ECOIZ

ECOIZ is a team project with a user-facing app, admin web, backend, database setup, and AI workstream.

## Project Structure

- `admin-web/` - admin panel frontend built with Next.js
- `database/` - Prisma schema, seed data, and PostgreSQL Docker setup
- `backend/` - planned main application backend
- `app-web/` - planned user-facing frontend
- `ai/` - planned AI module and integrations

At the moment, the repository already contains:

- `admin-web/`
- `database/`

The rest of the modules can be added later as separate folders in the same repository.

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
- Prisma
- PostgreSQL
- Docker

## Run Database

```bash
cd database
docker compose up -d
npm install
npx prisma migrate dev
npm run seed
```

Optional Prisma Studio:

```bash
npx prisma studio
```

## Run Admin Web

```bash
cd admin-web
npm install
npm run dev
```

Open:

- `http://localhost:3000`

Mock admin accounts:

- `akmaral@ecoiz.app / admin123`
- `nurdana@ecoiz.app / moderator123`

## Notes

- `admin-web` currently supports both `mock` and `live` API modes.
- `database` contains the source of truth for Prisma schema and seed data.
- Some frontend mock data is intentionally simplified during UI development, but key datasets should stay aligned with the database when possible.
