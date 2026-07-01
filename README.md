# Expense Tracker with Smart DSA Engine

This repository contains a production-ready scaffold for an expense tracking web application.

## Project structure

### `backend/`
- `app/` — Flask application package.
- `app/config.py` — environment-based configuration for Flask, SQLAlchemy, JWT, and CORS.
- `app/__init__.py` — app factory that initializes extensions and registers blueprints.
- `app/models/` — SQLAlchemy models for users, expenses, and categories.
- `app/controllers/` — MVC controllers for routing logic.
- `app/routes/` — Flask blueprints and route registration.
- `app/schemas/` — Marshmallow schemas and validation.
- `app/services/` — domain service stubs for DSA engine helpers.
- `app/middleware/` — centralized error handling and middleware registration.
- `app/utils/` — response helpers and shared decorators.
- `instance/` — local SQLite database file location.
- `requirements.txt` — backend Python dependencies.

### `frontend/`
- `src/` — React application source code.
- `src/App.jsx` — application router and top-level page assembly.
- `src/main.jsx` — Vite bootstrap for React.
- `src/pages/` — page-level route components.
- `src/components/` — reusable UI components and layout pieces.
- `src/services/` — Axios API wrapper and client service abstractions.
- `src/context/` — React context providers for auth and expense state.
- `src/hooks/` — custom hooks for reusable behavior.
- `src/utils/` — frontend constants and helper utilities.
- `package.json` — frontend dependencies and scripts.
- `vite.config.js` — Vite build and dev server configuration.

## Environment configuration

Create a `.env` file from `.env.example` and set your local credentials.

## Notes

This scaffold sets up the full backend and frontend folder structure, configures Flask, React, database connection, JWT, and CORS. Feature implementation is intentionally deferred.
