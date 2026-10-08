# Meetly

## Project overview

Meetly is a Zoom-inspired meeting workspace built for the Scaler full-stack assignment. It supports instant meetings, scheduled meetings, invitation links, join validation, persisted participants, and a polished responsive meeting room.

## Features

The dashboard is seeded with realistic upcoming and recent meetings. Users can create an instant meeting, schedule a future meeting, copy its invitation link, join using either a link or normalized meeting ID, and use the responsive meeting-room controls and people panel.

## Tech stack

- Frontend: Next.js 15, React, TypeScript, Lucide icons
- Backend: FastAPI, SQLAlchemy, Pydantic
- Database: SQLite (a relational schema for users, meetings, and participants)

## Architecture

The Next.js App Router frontend is a client-side meeting workspace backed by a typed API client. FastAPI owns validation, meeting-ID generation, and persistence. SQLAlchemy stores users, meetings, and participants in SQLite; initialization and idempotent seed data run at backend startup.

## Database schema

`users` stores the default host, `meetings` stores unique meeting IDs, scheduling, invitation URLs, host ownership, and status, and `participants` records meeting membership, timestamps, and host state. Foreign keys connect meetings to users and participants to meetings; unique and scheduling indexes support lookup and dashboard queries.

## Project structure

```
backend/app/     FastAPI application, models, schema, seed logic
frontend/app/    Next.js pages and global UI
frontend/components/ reusable dialogs and branding
frontend/lib/    typed API client
```

## Local setup

Use two terminals. Python 3.10+ and Node 20+ are recommended.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend
copy .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`. The API docs are available at `http://localhost:8000/docs`.

## Environment variables

| Location | Variable | Default |
| --- | --- | --- |
| backend | `DATABASE_URL` | `sqlite:///./zoomish.db` |
| backend | `FRONTEND_BASE_URL` | `http://localhost:3000` |
| frontend | `NEXT_PUBLIC_API_URL` | `http://localhost:8000` |

The database is initialized and idempotently seeded when the backend starts; no separate seed command is needed.

## API endpoints

- `GET /api/meetings`, `/upcoming`, `/recent`, `/{meeting_id}`
- `POST /api/meetings/instant`, `/schedule`, `/join`
- `GET/POST /api/meetings/{meeting_id}/participants`
- `DELETE /api/meetings/{meeting_id}/participants/{participant_id}`

## How to seed the database

No manual command is required. The backend creates tables and inserts seed data on first startup; the seeder is idempotent.

## How to test

Run `npm run lint`, `npm run typecheck`, and `npm run build` inside `frontend`. Run `python -m compileall app` inside `backend`. Start the API and use `http://localhost:8000/docs` to inspect the OpenAPI endpoints.

## Deployment instructions

Deploy `frontend` to Vercel with `NEXT_PUBLIC_API_URL` set to the public API URL. Deploy `backend` to Render, Railway, or a comparable Python service with `FRONTEND_BASE_URL` set to the Vercel URL. SQLite is suitable for this assignment, but a cloud deployment requires a persistent volume or a managed relational database for durable data.

## Assumptions

Authentication is intentionally omitted because the assignment explicitly excludes it. A default host account supplies the no-login experience.

## Design decisions

Meeting IDs are cryptographically random nine-digit values formatted for readability. The interface uses original, Zoom-inspired styling and browser-safe UI controls without proprietary assets.

## Known limitations

The meeting room supplies a robust conferencing UI and workflow but does not include WebRTC/SFU/TURN infrastructure, which is outside the mandatory scope.

## Future improvements

Add authenticated accounts, WebRTC signaling and media infrastructure, calendar integrations, and role-based moderation for a production deployment.
