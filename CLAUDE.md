# FitCoach AI — Claude Assistant Guide

## Current Status
> Last updated: 2026-02-23

| Area | Status |
|---|---|
| Backend foundation | ✅ Complete and tested |
| Auth endpoints | ✅ Working — `register`, `login`, `refresh`, `logout` |
| AI module | ⚠️ Stubs only — `client`, `context_builder`, `token_budget`, all prompts |
| Service layer | ⚠️ Stubs only — `pr`, `workout`, `body_stats`, `recovery`, `report` |
| Test suite | ✅ 5/5 passing (health check + 4 auth tests) |
| Frontend | ❌ Not started |

### What's wired up
- FastAPI app starts cleanly with all routers registered
- Auth flow (JWT + bcrypt + refresh tokens) is fully functional
- SQLite used for local dev; all models/migrations scaffolded
- `tests/conftest.py` provides a per-test in-memory SQLite `AsyncClient` fixture

### Package manager
Use **`uv`** for all Python commands — not `pip`:
```bash
uv sync --extra dev   # install deps
uv run pytest tests/ -v
uv run uvicorn app.main:app --reload --port 8000
```

---

## Project Overview
FitCoach AI is a production-quality fitness coaching web application with AI-powered personalization via OpenAI API. Features: workout tracking, nutrition planning, progress reporting, recovery tracking, hydration logging, and personal records.

## Tech Stack
| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.12+) |
| Frontend | Next.js 14 (App Router) |
| Database | PostgreSQL (SQLite dev) |
| AI | OpenAI API (GPT-4o) |
| Auth | JWT + HttpOnly cookies + bcrypt |
| Styling | Tailwind CSS + shadcn/ui |
| Charting | Recharts |
| State | TanStack Query + Zustand |
| Background Jobs | Celery + Redis |
| ORM | SQLAlchemy 2.0 async + Alembic |

## Repository Structure
```
fitcoach-ai/
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── main.py           # FastAPI factory
│   │   ├── config.py         # Pydantic Settings
│   │   ├── dependencies.py   # DI: get_db, get_current_user
│   │   ├── core/             # database, security, redis
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic request/response
│   │   ├── routers/          # Thin FastAPI handlers
│   │   ├── services/         # Business logic
│   │   ├── ai/               # OpenAI integration
│   │   └── tasks/            # Celery background jobs
│   └── alembic/              # DB migrations
└── frontend/          # Next.js 14 application
    └── src/
        ├── app/              # App Router pages
        ├── components/       # React components
        ├── hooks/            # Custom React hooks
        ├── lib/              # API client, utilities
        ├── store/            # Zustand stores
        ├── types/            # TypeScript types
        └── providers/        # Context providers
```

## Architecture Decisions
- **Services layer**: All business logic in `services/`. Routers are thin—validate input, call service, return response.
- **Pydantic everywhere**: Use schemas for all request/response validation. Never use raw dicts in API responses.
- **JSONB for flexible data**: Use JSONB columns for equipment arrays, AI plan output, and other schema-flexible data.
- **Streaming pattern**: AI features stream via SSE. Backend uses FastAPI `StreamingResponse`, frontend proxy in Next.js API routes, client uses `useAIStream` hook.
- **Never call OpenAI SDK directly from routers**: Always go through `app/ai/` module.

## Development Commands
```bash
# Backend setup
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000

# Docker (full stack)
docker-compose up -d

# Migrations
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head

# Tests
uv run pytest --cov=app -v

# Linting
uv run ruff check app/
uv run ruff format app/

# Frontend
cd frontend
npm install
npm run dev      # port 3000
npm run build
npm run lint
npm run test
npm run test:e2e
```

## Environment Variables
See `.env.example` for all required variables:
- `DATABASE_URL` — PostgreSQL connection string
- `SECRET_KEY` — JWT signing secret (min 32 chars)
- `OPENAI_API_KEY` — OpenAI API key
- `REDIS_URL` — Redis connection URL
- `AWS_*` — S3 credentials for progress photos
- `FRONTEND_URL` — CORS origin

## Testing Approach
- **Backend**: `pytest` + `httpx.AsyncClient` for integration tests. Mock OpenAI API with `unittest.mock`.
- **Frontend**: Vitest for unit tests, Playwright for E2E.
- Coverage target: >80% backend.

## Code Conventions

### Python
- Use `async def` for all route handlers and service methods.
- Type-annotate all function signatures.
- Use `from __future__ import annotations` in all files.
- Services raise `HTTPException` only for client errors; log server errors.
- Never commit database sessions in service methods—let the router/DI handle it.

### TypeScript
- Strict mode enabled. No `any` types.
- Use `interface` for API response shapes, `type` for unions/utilities.
- All API calls through `src/lib/api.ts` — never raw `fetch` in components.

## API Design Conventions
- All routes prefixed `/api/v1/`
- Paginated lists: `{ data: T[], total: int, page: int, page_size: int, pages: int }`
- Errors: `{ error: { code: string, message: string } }`
- Auth: Bearer token in Authorization header (from HttpOnly cookie via middleware)
- UUIDs for all PKs

## Git Conventions (Conventional Commits)
```
feat: add PR celebration modal
fix: correct recovery score calculation
refactor: extract TDEE logic to nutrition_service
docs: update API endpoint docs
test: add workout session integration tests
```

## Key Business Logic

### PR Detection (pr_service.py)
After every logged set, check if `weight_kg > previous max` OR `reps > max at this weight`. Create `PersonalRecord` with `celebrated=False`. Frontend polls `/personal-records/pending-celebrations` post-session.

### Recovery Score (recovery_service.py)
0–100 composite score:
- Sleep hours vs 7–9h target: 40%
- Sleep quality 1–5: 20%
- Inverse fatigue 1–10: 25%
- Training load past 3 days: 15%

### TDEE (nutrition_service.py)
Mifflin-St Jeor BMR → activity multiplier → goal adjustment (deficit/surplus). Always include user's `units` preference in AI prompts.

### Strength Score (body_stats_service.py)
0–1000 composite across 5 lifts: squat, bench, deadlift, OHP, row. Normalized by bodyweight and gender percentile tables.

## Common Pitfalls
- **Never commit DB session in services** — services receive `AsyncSession` from DI, call `await session.flush()` if needed, but let the router commit.
- **No JWTs in localStorage** — use HttpOnly cookies only. Tokens exposed via XSS if in localStorage.
- **Always include user units in AI prompts** — users set kg/lbs preference; AI must match.
- **S3 direct uploads** — generate presigned URLs server-side; never proxy large files through the backend.
- **Token budget** — check `token_budget.py` before every OpenAI call; raise 429 if daily limit exceeded.
