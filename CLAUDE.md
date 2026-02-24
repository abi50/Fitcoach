# FitCoach AI — Claude Assistant Guide

## Current Status
> Last updated: 2026-02-24 — Full product redesign started

| Area | Status |
|---|---|
| Backend auth + DB | ✅ Carried forward — JWT, bcrypt, SQLite dev |
| Backend services | ✅ Carried forward — workout, nutrition, recovery, PR detection |
| Backend AI module | ⚠️ Needs rewrite — new prompt architecture |
| Frontend | 🔄 Full redesign — new landing page, AI builders, dashboard |
| Landing page | 🔜 Next |
| AI Workout Builder | 🔜 Next |
| AI Meal Plan Builder | 🔜 Next |
| Registration / Login | 🔜 Next |
| Personal Dashboard | 🔜 Next |

---

## Product Vision

FitCoach AI is a **beautiful, fun, and clear** fitness web app for athletes. When a user lands on the site they immediately understand what to do.

### Guest Flow (not logged in)
- Beautiful landing page that explains the app clearly
- Two main CTAs: **"Build My Workout Plan"** and **"Build My Meal Plan"**
- Guest can use AI features and preview full results
- To SAVE anything → must register (soft gate)

### Core Features

**1. AI Workout Plan Builder**
- User fills a form: age, fitness level, training experience, goals (strength / weight loss / muscle gain), available equipment, days per week
- OR conversational flow where AI asks questions one by one
- GPT-4o generates a personalized weekly workout plan (structured JSON → rendered beautifully)
- User can download the plan as PDF
- Logged-in users: plan saved to profile

**2. AI Meal Plan Builder**
- Based on workout plan + personal data (weight, height, goal)
- GPT-4o generates daily meal plan with macros
- Download as PDF or save to profile

**3. Personal Dashboard (logged-in)**
- Workout history and progress tracking
- Personal records (PRs) with celebrations
- Recovery score
- Body stats over time
- Upcoming workouts from their saved plan

---

## Design Requirements
- Modern, clean, motivating athletic aesthetic
- Mobile-first responsive
- Clear visual hierarchy — user always knows what to do next
- Fun micro-interactions and animations (Framer Motion)
- Design in Figma MCP first, then implement

---

## Tech Stack
| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.12+) |
| Frontend | Next.js 14 (App Router) |
| Database | PostgreSQL (SQLite dev) |
| AI | OpenAI API (GPT-4o) — streaming via SSE |
| Auth | JWT + HttpOnly cookies + bcrypt |
| Styling | Tailwind CSS + shadcn/ui |
| Animation | Framer Motion |
| Charting | Recharts |
| State | TanStack Query + Zustand |
| PDF | react-pdf or @react-pdf/renderer |
| ORM | SQLAlchemy 2.0 async + Alembic |

---

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
│   │   ├── ai/               # OpenAI integration + prompts
│   │   └── tasks/            # Celery background jobs
│   └── alembic/              # DB migrations
└── frontend/          # Next.js 14 application
    └── src/
        ├── app/              # App Router pages
        │   ├── page.tsx              # Landing page
        │   ├── workout-builder/      # AI workout plan builder
        │   ├── meal-builder/         # AI meal plan builder
        │   ├── login/
        │   ├── register/
        │   └── dashboard/            # Logged-in dashboard
        ├── components/
        │   ├── landing/              # Hero, Features, CTA sections
        │   ├── builders/             # Form + conversational AI widgets
        │   ├── plan-display/         # Rendered workout/meal plans
        │   ├── dashboard/            # Dashboard widgets
        │   └── ui/                   # shadcn/ui base components
        ├── hooks/            # useAIStream, usePlanBuilder, etc.
        ├── lib/              # API client, PDF utils
        ├── store/            # Zustand: auth, plan draft
        ├── types/            # TypeScript interfaces
        └── providers/        # QueryProvider, ThemeProvider
```

---

## Architecture Decisions

### Guest-first AI
- All AI builder pages are accessible without login
- Plan is generated and displayed in-session (stored in Zustand `planDraft` store)
- Saving triggers a soft gate: show register modal, then persist on success
- Never store draft in DB until user is authenticated

### AI Integration Pattern
- Backend endpoint: `POST /api/v1/ai/workout-plan` → streams NDJSON via SSE
- Frontend: `useAIStream` hook consumes the stream, builds plan object progressively
- Structured output: GPT-4o responds with JSON schema (function calling / response_format)
- Never call OpenAI SDK directly from routers — always through `app/ai/` module

### Streaming Pattern
- Backend uses FastAPI `StreamingResponse` with `text/event-stream`
- Frontend proxy in Next.js API routes (avoids CORS and exposes OPENAI_API_KEY)
- Client uses `useAIStream` hook

### PDF Generation
- Client-side: `@react-pdf/renderer` renders plan as downloadable PDF
- No server-side PDF generation needed

---

## Development Commands
```bash
# Backend
cd backend
uv sync --extra dev
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000

# Tests
uv run pytest tests/ -v
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
```

---

## Environment Variables
```
DATABASE_URL=sqlite+aiosqlite:///./dev.db
SECRET_KEY=<min 32 chars>
OPENAI_API_KEY=<key>
FRONTEND_URL=http://localhost:3000
```

---

## Build Order (feature-by-feature)

1. **Landing page** — hero, features section, two CTA buttons, mobile-first
2. **AI Workout Builder** — form flow, streaming GPT-4o response, plan display, PDF download
3. **Auth pages** — register + login, hooked to save plan draft on success
4. **AI Meal Builder** — same pattern as workout builder
5. **Personal Dashboard** — workout history, PRs, recovery score, upcoming plan

---

## Code Conventions

### Python
- `async def` for all route handlers and service methods
- Type-annotate all function signatures
- `from __future__ import annotations` in all files
- Services raise `HTTPException` only for client errors
- Never commit DB sessions in services — let the router/DI handle it

### TypeScript
- Strict mode. No `any` types.
- `interface` for API response shapes, `type` for unions/utilities
- All API calls through `src/lib/api.ts`
- All AI streaming through `useAIStream` hook

### API Design
- All routes prefixed `/api/v1/`
- Errors: `{ error: { code: string, message: string } }`
- Auth: Bearer token in Authorization header
- UUIDs for all PKs

---

## Git Conventions (Conventional Commits)
```
feat: add AI workout builder streaming endpoint
feat: landing page hero section
fix: SSE stream closes prematurely on slow connections
refactor: extract plan schema to shared types
```

---

## Key Business Logic

### AI Workout Plan (ai/workout_prompt.py)
Input: `{ age, fitness_level, experience_years, goal, equipment[], days_per_week }`
Output: structured JSON — `{ plan_name, weekly_schedule: [{ day, exercises: [{ name, sets, reps, rest_s, notes }] }], notes }`
GPT-4o call uses `response_format: { type: "json_object" }` for reliable parsing.

### AI Meal Plan (ai/meal_prompt.py)
Input: `{ weight_kg, height_cm, age, goal, activity_level, dietary_restrictions[] }`
Calculates TDEE via Mifflin-St Jeor + activity multiplier server-side, passes target calories/macros to GPT-4o.
Output: `{ daily_calories, macros: { protein_g, carbs_g, fat_g }, meals: [{ name, foods[], calories }] }`

### PR Detection (services/pr_service.py)
After every logged set: check if `weight_kg > previous max` OR `reps > max at this weight`.
Create `PersonalRecord` with `celebrated=False`. Frontend polls `/personal-records/pending-celebrations`.

### Recovery Score (services/recovery_service.py)
0–100 composite: sleep hours (40%), sleep quality (20%), inverse fatigue (25%), training load (15%).

---

## Common Pitfalls
- **Never commit DB session in services** — flush if needed, let router commit
- **No JWTs in localStorage** — HttpOnly cookies only
- **Guest plan draft** — store in Zustand only; write to DB only after auth
- **Token budget** — check `token_budget.py` before every OpenAI call; raise 429 if exceeded
- **Turbopack TLS** — `next.config.ts` must have `experimental.turbopackUseSystemTlsCerts: true`
- **shadcn toast** — use `sonner`, not the deprecated `toast` component
