# Meetly

A Zoom-inspired meeting workspace built for the Scaler full-stack assignment. It supports instant meetings, scheduled meetings, invitation links, join validation, persisted participants, and a polished responsive meeting room.

## Tech stack

- Frontend: Next.js 15, React, TypeScript, Lucide icons
- Backend: FastAPI, SQLAlchemy, Pydantic
- Database: SQLite (a relational schema for users, meetings, and participants)

## Features

- Dashboard with seeded upcoming and recent meetings
- Instant meeting creation with secure random `123 456 789` IDs
- Scheduled meetings with validation and immediate dashboard updates
- Join via normalized ID or full invitation URL, with a display name
- Persisted SQLite data and participant records
- Responsive meeting room with invite copy, people panel, and media/control UI

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

## Testing and deployment

Run `npm run build` for a production frontend check. Start the backend with Uvicorn; its OpenAPI docs provide endpoint verification. Deploy the frontend to Vercel with `NEXT_PUBLIC_API_URL` set to the backend URL. Deploy FastAPI to Render/Railway with `FRONTEND_BASE_URL` set to the Vercel URL. SQLite is suitable for this assignment, but production cloud deployments need a persistent volume or managed relational database.

Authentication is intentionally omitted because the assignment explicitly excludes it. The meeting room supplies a robust conferencing UI and workflow but does not include WebRTC/SFU/TURN infrastructure, which is outside the mandatory scope.
