# 💰 Expense Tracker with Smart DSA Engine

A modern full-stack Expense Tracker built using **React**, **Flask**, and **PostgreSQL**, enhanced with Data Structures & Algorithms for efficient searching, sorting, analytics, and undo functionality.

## 🚀 Live Demo

**Frontend:** https://expense-tracker-with-smart-dsa-engi.vercel.app

**Backend API:** https://expense-tracker-with-smart-dsa-engine.onrender.com

---

# ✨ Features

## 🔐 Authentication
- User Registration
- Secure Login & Logout
- JWT Authentication
- Password Hashing (bcrypt)
- Token Revocation (JWT Blocklist)

---

## 💸 Expense Management

- Add Expenses
- Edit Expenses
- Delete Expenses
- View Expense History
- Category-wise Expenses
- Payment Mode Tracking
- Undo Last Operation (Stack)

---

## 💵 Income Management

- Add Income
- Edit Income
- Delete Income
- Undo Last Operation

---

## 📊 Dashboard

- Total Income
- Total Expenses
- Current Balance
- Recent Transactions
- Top Spending Category
- Savings Rate

---

## 📈 Analytics

- Monthly Expense Summary
- Category-wise Analytics
- Dashboard Statistics
- Financial Overview

---

## 🔍 Smart Searching

Implemented using Data Structures & Algorithms.

### Linear Search

- Search by Title
- Search by Description
- Search by Category

### Binary Search

- Search by Expense ID
- Search by Date
- Search within Date Range

---

## 📑 Smart Sorting

- Sort by Amount
- Sort by Date
- Sort by Category
- Sort by Title
- Multi-field Sorting

---

## ↩️ Undo System

Implemented using **Stack (LIFO)**

Supports undo for:

- Expense Creation
- Expense Update
- Expense Deletion

Maximum stack size per user:
- 10 Operations

---

## 🛡 Security

- JWT Access Tokens
- Refresh Tokens
- Password Hashing
- Protected API Routes
- Environment Variables
- CORS Protection

---

# 🛠 Tech Stack

## Frontend

- React
- Vite
- React Router
- Context API
- Axios
- Tailwind CSS
- React Icons

---

## Backend

- Flask
- SQLAlchemy
- Marshmallow
- Flask-JWT-Extended
- Flask-Migrate
- Gunicorn

---

## Database

- PostgreSQL (Production)
- SQLite (Development)

---

## Deployment

- Frontend → Vercel
- Backend → Render
- Database → Render PostgreSQL

---

# 📂 Project Structure

```
Expense-Tracker/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── controllers/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── schemas/
│   │   └── utils/
│   │
│   ├── migrations/
│   ├── tests/
│   ├── wsgi.py
│   └── requirements.txt
│
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/expense-tracker.git

cd expense-tracker
```

---

# Backend Setup

```bash
cd backend

python -m venv venv

source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create `.env`

```env
SECRET_KEY=your_secret_key

JWT_SECRET_KEY=your_jwt_secret

DATABASE_URL=sqlite:///expense_tracker.db
```

Run database migrations

```bash
flask db upgrade
```

Run backend

```bash
python run.py
```

---

# Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

# Production Deployment

## Frontend

Deploy on **Vercel**

```bash
npm run build
```

---

## Backend

Deploy on **Render**

Uses

- Gunicorn
- PostgreSQL
- Environment Variables

---

# REST API

## Authentication

| Method | Endpoint |
|----------|---------------------------|
| POST | `/api/auth/register` |
| POST | `/api/auth/login` |
| POST | `/api/auth/logout` |
| POST | `/api/auth/forgot-password` |
| POST | `/api/auth/verify-otp` |
| POST | `/api/auth/reset-password` |

---

## Expenses

| Method | Endpoint |
|----------|---------------------------|
| GET | `/api/expenses/` |
| POST | `/api/expenses/` |
| PUT | `/api/expenses/{id}` |
| DELETE | `/api/expenses/{id}` |

---

## Income

| Method | Endpoint |
|----------|---------------------------|
| GET | `/api/incomes/` |
| POST | `/api/incomes/` |
| PUT | `/api/incomes/{id}` |
| DELETE | `/api/incomes/{id}` |

---

## Analytics

| Method | Endpoint |
|----------|---------------------------|
| GET | `/api/analytics/dashboard` |

---

# Data Structures & Algorithms Used

| Feature | Algorithm / Data Structure |
|-----------|----------------------------|
| Undo | Stack |
| Search by Title | Linear Search |
| Search by Description | Linear Search |
| Search by Category | Linear Search |
| Search by ID | Binary Search |
| Search by Date | Binary Search |
| Sorting | Python TimSort |
| Multi-field Sorting | Custom Sorting Logic |

---

# Testing

- Backend Unit Tests
- Authentication Testing
- CRUD Testing
- Search Testing
- Sorting Testing
- Analytics Testing

---

# Future Improvements

- AI Expense Prediction
- OCR Receipt Scanner
- Email Reports
- Budget Notifications
- Mobile Application
- Cloud Storage Integration
- Export Reports (PDF/Excel)

---

# Author

**Kabyik Paul**

B.Tech – Computer Science Engineering (IoT & Cyber Security)

Heritage Institute of Technology

---

# License

This project is developed for educational purposes.
