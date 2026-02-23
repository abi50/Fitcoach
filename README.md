# FitCoach AI

AI-powered fitness coaching web application for athletes and gym-goers.

## Features
- AI workout plan generation (Claude-powered, streaming)
- Manual workout tracking with session logger
- Personal records detection with celebration animations
- Nutrition planning with macro tracking and AI meal plans
- Recovery tracking (sleep, soreness, recovery score)
- Hydration logging with daily targets
- Progress charts (weight, strength, body measurements)
- Weekly/monthly PDF reports

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.12+
- uv (Python package manager)

### Setup
```bash
cp .env.example .env
# Fill in your ANTHROPIC_API_KEY and other values

docker-compose up -d

# Backend
cd backend
uv sync
uv run alembic upgrade head

# Frontend
cd frontend
npm install
npm run dev
```

### Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Tech Stack
- **Backend**: FastAPI + PostgreSQL + SQLAlchemy + Alembic
- **Frontend**: Next.js 14 + Tailwind CSS + shadcn/ui
- **AI**: Anthropic Claude (opus for plans, haiku for suggestions)
- **Jobs**: Celery + Redis

## Development
See [CLAUDE.md](CLAUDE.md) for full development guide.
