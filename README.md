# Expense Tracker with Smart DSA Engine

A full-stack expense tracking application with a Flask backend that integrates custom data-structure implementations (merge sort, search, stack, hash table) into real API endpoints.

## What's implemented

### Backend (ready to run)
- **Auth** — register, login, JWT refresh, profile, password reset
- **Expenses** — CRUD, merge sort, linear/binary search, undo stack, hash-table summaries
- **Incomes** — CRUD
- **Analytics** — overview, categories, time series, dashboard
- **Tests** — 120+ pytest cases

### Frontend (scaffold)
- React + Vite + Tailwind project structure
- Axios client with JWT interceptors (`src/services/api.js`)
- Pages and components are placeholders — UI not built yet

## Quick start

### 1. Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

API runs at `http://localhost:5000`.

### 2. Frontend (optional)

```powershell
cd frontend
npm install
npm run dev
```

UI runs at `http://localhost:5173` and proxies `/api` to the Flask server.

### 3. Run tests

```powershell
cd backend
.venv\Scripts\activate
pytest tests/ -v
```

## Environment variables

Copy `backend/.env.example` to `backend/.env`:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask secret (use 32+ characters in production) |
| `JWT_SECRET_KEY` | JWT signing key (use 32+ characters in production) |
| `DATABASE_URL` | SQLite by default |
| `CORS_ORIGINS` | Allowed frontend origin(s) |
| `FLASK_ENV` | `development`, `testing`, or `production` |

## API overview

| Prefix | Description |
|--------|-------------|
| `/api/auth` | Authentication |
| `/api/expenses` | Expenses + DSA features (sort, search, undo, summaries) |
| `/api/incomes` | Income tracking |
| `/api/analytics` | Spending analytics |
| `/api/categories` | Reserved (routes not yet implemented) |

## DSA engine

| Structure | Module | Used for |
|-----------|--------|----------|
| Merge sort | `services/merge_sort.py` | Expense sorting |
| Linear/binary search | `services/search.py` | Expense search |
| Stack | `services/stack.py` | Undo history (max 10 per user) |
| Hash table | `services/hash_table.py` | Per-user category/monthly summaries |

See `backend/MERGE_SORT_GUIDE.md`, `SEARCH_GUIDE.md`, and `STACK_GUIDE.md` for details.

## Project structure

```
backend/
  app/           Flask application (routes, controllers, models, services)
  tests/         pytest suite
  run.py         Entry point
frontend/
  src/           React source (scaffold)
```
