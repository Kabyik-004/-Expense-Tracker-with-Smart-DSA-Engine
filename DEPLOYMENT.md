# Deployment Guide

## Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL (production) or SQLite (development)
- Domain name + SSL certificate (production)
- Docker (optional, for containerized deployment)

---

## 1. Environment Variables

### Backend (`backend/.env`)

```env
# Required — generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=<64-char-random-string>
JWT_SECRET_KEY=<different-64-char-random-string>

# Database — PostgreSQL for production
DATABASE_URL=postgresql://user:password@host:5432/expense_tracker

# Flask
FLASK_ENV=production

# JWT expiry
JWT_ACCESS_HOURS=1
JWT_REFRESH_DAYS=30

# CORS — comma-separated origins
CORS_ORIGINS=https://your-domain.com

# Gunicorn (optional)
GUNICORN_WORKERS=4
GUNICORN_BIND=0.0.0.0:8000
```

### Frontend (`frontend/.env.production`)

```env
VITE_API_URL=/api
```

For separate frontend/backend domains:
```env
VITE_API_URL=https://api.your-domain.com
```

---

## 2. Render

### Web Service (Backend)

1. **Create a New Web Service**
   - Connect your GitHub repo
   - **Name:** `expense-tracker-api`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app --config gunicorn.conf.py`
   - **Root Directory:** `backend/`

2. **Set Environment Variables** (in Render dashboard)
   - `SECRET_KEY`, `JWT_SECRET_KEY` — random hex strings
   - `DATABASE_URL` — from Render PostgreSQL
   - `FLASK_ENV` — `production`
   - `CORS_ORIGINS` — your frontend URL
   - `JWT_BLOCKLIST_ENABLED` — `true`

3. **Add PostgreSQL Database**
   - Create a Render PostgreSQL instance
   - Copy its internal connection string into `DATABASE_URL`
   - (Render auto-migrates—your app calls `db.create_all()` on startup)

### Static Site (Frontend)

1. **Create a New Static Site**
   - Connect same repo
   - **Name:** `expense-tracker-ui`
   - **Root Directory:** `frontend/`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`

2. **Set Environment Variable**
   - `VITE_API_URL` — your Render backend URL, e.g. `https://expense-tracker-api.onrender.com`

3. **Redirect Rules** (for client-side routing)
   - Source: `/*`
   - Destination: `/index.html`
   - Status: `200`

---

## 3. Railway

### Backend

1. **Create a New Project** → **Deploy from GitHub repo**
2. **Set Root Directory** to `backend/`
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `gunicorn wsgi:app --config gunicorn.conf.py`
5. **Healthcheck Path:** `/api/auth/validate` (requires no auth)
6. **Add Environment Variables** (same as Render section)

### Database

- Add a **PostgreSQL** plugin in Railway
- Railway auto-injects `DATABASE_URL` into your backend service

### Frontend

1. Add a second service in the same project
2. **Root Directory:** `frontend/`
3. **Build Command:** `npm install && npm run build`
4. **Start Command:** `npx serve dist -s -l $PORT`
5. Set `VITE_API_URL` to your backend Railway URL

---

## 4. Vercel (Frontend only)

Vercel hosts static sites and can proxy `/api` to your backend.

1. **Import** your GitHub repo
2. **Root Directory:** `frontend/`
3. **Build Command:** `npm install && npm run build`
4. **Output Directory:** `dist`
5. **Environment Variable:** `VITE_API_URL=/api`

### Vercel API Proxy (`frontend/vercel.json`)

```json
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "https://your-backend.com/api/$1" },
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

This enables SPA routing *and* proxies API calls to your backend.

---

## 5. Docker Deployment

### Build and run (single server, same-origin)

```bash
# 1. Build frontend
cd frontend
npm install && npm run build
cd ..

# 2. Set secrets (or use your .env)
$env:SECRET_KEY = "your-64-char-secret"
$env:JWT_SECRET_KEY = "your-64-char-jwt-secret"

# 3. Start with Docker Compose
docker compose up -d --build
```

This starts three services:
| Service | Port | Description |
|---------|------|-------------|
| `nginx`  | 80/443 | Reverse proxy + static files |
| `api`    | 8000   | Flask + Gunicorn |
| `db`     | 5432   | PostgreSQL |

### Manual Docker build

```bash
docker build -t expense-tracker .
docker run -p 8000:8000 \
  -e SECRET_KEY=... \
  -e JWT_SECRET_KEY=... \
  -e DATABASE_URL=postgresql://... \
  -e CORS_ORIGINS=https://your-domain.com \
  expense-tracker
```

---

## 6. Manual Server Deployment (Ubuntu/Debian)

### Backend

```bash
# Install system deps
sudo apt update
sudo apt install -y python3-pip python3-venv postgresql nginx

# Clone & setup
git clone https://github.com/your-org/expense-tracker.git /opt/expense-tracker
cd /opt/expense-tracker/backend

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Copy env
cp .env.example .env
# EDIT .env with your secrets and PostgreSQL URL

# Run migrations (creates tables)
python -c "from wsgi import app; print('Tables ready')"

# Test
gunicorn wsgi:app --config gunicorn.conf.py --daemon
```

### Systemd Service (`/etc/systemd/system/expense-tracker.service`)

```ini
[Unit]
Description=Expense Tracker API
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/expense-tracker/backend
EnvironmentFile=/opt/expense-tracker/backend/.env
ExecStart=/opt/expense-tracker/backend/.venv/bin/gunicorn wsgi:app --config gunicorn.conf.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable expense-tracker
sudo systemctl start expense-tracker
```

### Frontend

```bash
cd /opt/expense-tracker/frontend
npm install
npm run build
sudo cp -r dist/* /var/www/expense-tracker/frontend/dist/
```

### Nginx

Copy `nginx/expense-tracker.conf` to `/etc/nginx/sites-available/`:

```bash
sudo cp /opt/expense-tracker/nginx/expense-tracker.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/expense-tracker.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

## 7. Post-Deployment Checklist

- [ ] Generate strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Use PostgreSQL (not SQLite) in production
- [ ] Set `FLASK_ENV=production`
- [ ] Configure CORS to your actual frontend domain
- [ ] Enable HTTPS (Let's Encrypt / Cloudflare)
- [ ] Verify JWT token blocklist works:
      `curl -X POST https://your-domain.com/api/auth/logout -H "Authorization: Bearer <token>"`
      Then reuse the same token — should get 401
- [ ] Run backend tests: `pytest tests/ -v`
- [ ] Run frontend build: `npm run build`
- [ ] Monitor logs: `journalctl -u expense-tracker -f`

---

## 8. Troubleshooting

| Problem | Solution |
|---------|----------|
| `connection refused` to PostgreSQL | Check `DATABASE_URL`, network rules, and pg_hba.conf |
| CORS errors in browser | Verify `CORS_ORIGINS` matches exact frontend origin (no trailing slash) |
| Token revoked immediately | Ensure `JWT_SECRET_KEY` matches between sessions (don't rotate without invalidating old tokens) |
| `db.create_all()` not running | Flask creates tables on first request — call any endpoint or run manually via `python -c "from wsgi import app"` |
| Static files 404 | Verify `root` in nginx config points to the built `dist/` directory |
| Routes always return `index.html` | This is expected for SPA — nginx `try_files` handles it correctly |
