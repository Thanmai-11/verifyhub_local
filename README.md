# VerifyHub 🔍
### A Peer-Verified Skills Platform

> **Don't just claim skills — prove them.**

VerifyHub is a full-stack Django web application where professionals upload evidence of their skills and verified peers review, vote on, and approve their submissions. Build a professional profile backed by real proof.

[![Tests](https://github.com/Thanmai-11/verifyhub_local/actions/workflows/tests.yml/badge.svg)](https://github.com/Thanmai-11/verifyhub_local/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/Thanmai-11/verifyhub_local/branch/main/graph/badge.svg)](https://codecov.io/gh/Thanmai-11/verifyhub_local)
![Python](https://img.shields.io/badge/Python-3.14-blue)
![Django](https://img.shields.io/badge/Django-6.0-green)
![Azure](https://img.shields.io/badge/Deployed-Azure-0089D6)
![Render](https://img.shields.io/badge/Deployed-Render-46E3B7)

---

## 🌐 Live Deployments

| Platform | URL | Status |
|----------|-----|--------|
| **Azure App Service** | https://verifyhub-app.azurewebsites.net | ✅ Live |
| **Render** | https://verifyhub-wyep.onrender.com | ✅ Live |

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Testing](#-testing)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Deployment](#-deployment)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)

---

## ✨ Features

- **Skill Verification** — Upload PDF/file evidence for any skill
- **Peer Review System** — Verified peers vote to approve or reject submissions
- **2-Vote Threshold** — Artifacts require 2 approvals to become verified
- **Public Profiles** — Shareable skill profiles with interactive radar charts
- **Admin Dashboard** — Superusers can review all pending artifacts directly
- **Cloudinary Storage** — Persistent file storage that survives redeployments
- **Responsive UI** — Mobile-first design with hamburger navigation

---

## 🛠 Tech Stack

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.14 | Core language |
| Django | 6.0.4 | Web framework |
| Gunicorn | 25.3.0 | WSGI server |
| dj-database-url | 3.1.2 | Database URL parsing |
| Whitenoise | 6.12.0 | Static file serving |

### Database & Storage
| Service | Purpose |
|---------|---------|
| PostgreSQL (Neon) | Production database |
| SQLite | Local development database |
| Cloudinary | Media file storage (production) |

### Frontend
| Technology | Purpose |
|-----------|---------|
| Plus Jakarta Sans | Typography |
| Chart.js | Radar skill charts |
| Vanilla JS + jQuery | DOM interactions + AJAX voting |
| CSS Variables | Theming system |

### DevOps & Infrastructure
| Tool | Purpose |
|------|---------|
| GitHub Actions | CI/CD pipeline |
| Azure App Service | Primary cloud deployment |
| Render | Secondary deployment |
| Codecov | Code coverage reporting |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     CLIENT BROWSER                       │
└─────────────────┬───────────────────┬───────────────────┘
                  │                   │
        ┌─────────▼──────┐   ┌────────▼──────────┐
        │  Azure App     │   │   Render App       │
        │  Service       │   │   Service          │
        │  (centralindia)│   │  (US region)       │
        └─────────┬──────┘   └────────┬───────────┘
                  │                   │
                  └─────────┬─────────┘
                            │
              ┌─────────────▼─────────────┐
              │   Django Application       │
              │   ┌───────────────────┐   │
              │   │  Views / URLs     │   │
              │   │  Models / Signals │   │
              │   │  Forms / Admin    │   │
              │   └───────────────────┘   │
              └──────┬─────────────┬──────┘
                     │             │
        ┌────────────▼──┐   ┌──────▼──────────┐
        │  Neon          │   │   Cloudinary     │
        │  PostgreSQL    │   │   Media Storage  │
        │  (shared DB)   │   │   (shared files) │
        └────────────────┘   └─────────────────┘
```

### Database Schema

```
User ──────────────────────────────────────────┐
  │                                             │
  │ (contributor)                (voter)        │
  ▼                                             ▼
Artifact ─────────────────────────────────── Vote
  │  (skill_id)                    (artifact_id, voter_id)
  ▼                                unique_together constraint
Skill
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- pip
- Git

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/Thanmai-11/verifyhub_local.git
cd verifyhub_local

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create environment file
cp .env.example .env
# Edit .env with your values

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Start development server
python manage.py runserver
```

Open http://127.0.0.1:8000

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (optional — defaults to SQLite locally)
DATABASE_URL=postgresql://user:password@host/dbname

# Cloudinary (optional — defaults to local media storage)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

> The app auto-detects the environment — if Cloudinary vars are absent, it uses local file storage. If `DATABASE_URL` is absent, it uses SQLite.

---

## 🧪 Testing

### Test Suite Overview

| Test File | Type | Count | Description |
|-----------|------|-------|-------------|
| `core/tests.py` | Unit + Integration + Security + Fuzzy | 60 | Models, views, auth, CSRF, SQL injection, XSS, boundary |
| `core/test_playwright.py` | E2E Browser (local) | 22 | Full browser automation against local server |
| `core/test_smoke.py` | Smoke | 11 | Critical path verification |
| `core/test_accessibility.py` | Accessibility (WCAG) | 6 | axe-core WCAG 2 AA compliance |
| `core/test_compatibility.py` | Compatibility | 20 | Responsive design across viewports |
| `core/test_visual.py` | Visual Regression | 7 | Screenshot baseline comparison |
| `core/test_production.py` | HTTP Production | 29 | Functional + non-functional against live Azure |
| `core/test_e2e_production.py` | E2E Production | 24 | Playwright against live Azure URL |
| `locustfile.py` | Load Testing | — | 50 concurrent users, 0% failure rate |

**Total: 179 automated tests**

### Code Coverage

```
Name                  Stmts   Miss  Cover
-----------------------------------------
core/__init__.py          0      0   100%
core/admin.py            18      4    78%
core/apps.py              3      0   100%
core/forms.py            18      0   100%
core/models.py           45      1    98%
core/urls.py              3      0   100%
core/views.py            95      8    92%
-----------------------------------------
TOTAL                   182     13    93%
```

### Running Tests

```bash
# Django unit tests
python manage.py test core.tests

# Playwright E2E (requires running server)
python manage.py runserver &
pytest core/test_playwright.py -v

# Accessibility tests
pytest core/test_accessibility.py -v -s

# Smoke tests
pytest core/test_smoke.py -v

# Compatibility tests
pytest core/test_compatibility.py -v

# Visual regression tests
pytest core/test_visual.py -v

# Production tests (against live Azure)
pytest core/test_production.py -v

# E2E production tests
pytest core/test_e2e_production.py -v

# Load testing
locust -f locustfile.py --host=http://127.0.0.1:8000

# Code coverage
coverage run --source='core' manage.py test core.tests
coverage report
coverage html
open htmlcov/index.html
```

### Security Tests Included
- ✅ CSRF protection on all forms
- ✅ SQL injection prevention
- ✅ XSS prevention (script tag escaping)
- ✅ Authentication bypass prevention
- ✅ Self-voting prevention
- ✅ Invalid input fuzzing
- ✅ Boundary value testing

---

## ⚙️ CI/CD Pipeline

### GitHub Actions Workflows

#### 1. Test Suite (`tests.yml`)
Triggers on every push to `main`:

```
Push to main
    ↓
Install dependencies
    ↓
Run 60 Django unit tests
    ↓
Generate coverage report (93%)
    ↓
Upload to Codecov
```

#### 2. Azure Deployment (`main_verifyhub-app.yml`)
Triggers on every push to `main`:

```
Push to main
    ↓
Install dependencies
    ↓
Collect static files
    ↓
Create deployment ZIP
    ↓
Deploy to Azure App Service
```

---

## ☁️ Deployment

### Azure App Service

```bash
# Create resources
az group create --name verifyhub-rg --location centralindia
az appservice plan create --name verifyhub-plan --resource-group verifyhub-rg --sku F1 --is-linux
az webapp create --name verifyhub-app --resource-group verifyhub-rg --plan verifyhub-plan --runtime "PYTHON:3.12"

# Set environment variables
az webapp config appsettings set --name verifyhub-app --resource-group verifyhub-rg --settings \
    SECRET_KEY="..." DEBUG="False" ALLOWED_HOSTS="verifyhub-app.azurewebsites.net" \
    DATABASE_URL="..." CLOUDINARY_CLOUD_NAME="..." CLOUDINARY_API_KEY="..." CLOUDINARY_API_SECRET="..."

# Deploy
zip -r release.zip . --exclude "*.pyc" --exclude ".git/*" --exclude "venv/*"
az webapp deploy --name verifyhub-app --resource-group verifyhub-rg --src-path release.zip --type zip
```

### Render
Connected to GitHub — auto-deploys on every push to `main`.

### Environment Detection
The app automatically configures itself based on environment variables:

```
Cloudinary vars present? → Use Cloudinary for media
DATABASE_URL present?    → Use PostgreSQL
Otherwise               → Use SQLite + local media
```

---

## 📡 API Reference

### Vote Endpoint

```
POST /vote/
```

**Request (form-data):**
| Field | Type | Values |
|-------|------|--------|
| `artifact_id` | integer | ID of the artifact |
| `vote` | string | `"approve"` or `"reject"` |

**Response (JSON):**
```json
{
  "success": true,
  "approve_count": 2,
  "reject_count": 0,
  "new_status": "approved"
}
```

**Error responses:**
```json
{ "success": false, "error": "Cannot vote on your own artifact" }
{ "success": false, "error": "Not verified in this skill" }
{ "success": false, "error": "Invalid artifact ID" }
```

**Authentication:** Required (redirects to login if unauthenticated)

---

## 📁 Project Structure

```
verifyhub_local/
├── core/                          # Main Django app
│   ├── migrations/                # Database migrations
│   ├── templates/core/            # HTML templates
│   │   ├── base.html              # Base layout + nav
│   │   ├── home.html              # Landing page
│   │   ├── dashboard.html         # User dashboard
│   │   ├── login.html             # Login form
│   │   ├── register.html          # Register form
│   │   ├── upload_artifact.html   # Upload form
│   │   ├── review_queue.html      # Peer review UI
│   │   └── public_profile.html    # Radar chart profile
│   ├── admin.py                   # Admin with bulk approve/reject
│   ├── forms.py                   # Django forms
│   ├── models.py                  # Skill, Artifact, Vote
│   ├── urls.py                    # URL routing
│   ├── views.py                   # Request handlers
│   ├── tests.py                   # 60 unit/security/fuzzy tests
│   ├── test_playwright.py         # 22 E2E browser tests (local)
│   ├── test_smoke.py              # 11 smoke tests
│   ├── test_accessibility.py      # 6 WCAG accessibility tests
│   ├── test_compatibility.py      # 20 viewport/responsive tests
│   ├── test_visual.py             # 7 visual regression tests
│   ├── test_production.py         # 29 live production tests
│   └── test_e2e_production.py     # 24 E2E production tests
├── verifyhub/                     # Django project config
│   ├── settings.py                # Environment-aware settings
│   ├── urls.py                    # Root URL config
│   ├── wsgi.py                    # WSGI entry point
│   └── asgi.py                    # ASGI entry point
├── .github/workflows/
│   ├── tests.yml                  # CI test + coverage pipeline
│   └── main_verifyhub-app.yml     # Azure deploy pipeline
├── locustfile.py                  # Load testing scenarios
├── startup.sh                     # Azure startup script
├── build.sh                       # Render build script
├── requirements.txt               # Python dependencies
├── .coveragerc                    # Coverage configuration
└── manage.py                      # Django management
```

---

## 🔑 Key Design Decisions

**1. Signals for Status Updates**
Vote status changes use Django signals (`post_save`, `post_delete`) so artifact status always stays consistent regardless of how votes are modified.

**2. Environment-Aware Storage**
A single `settings.py` handles both local and production by detecting Cloudinary credentials at runtime — no separate settings files needed.

**3. Superuser Bootstrap**
Superusers bypass the skill verification requirement for voting, solving the chicken-and-egg problem of getting the first verified user.

**4. AJAX Voting**
The review queue uses AJAX for voting so the page doesn't reload — approved/rejected cards fade out smoothly after the 2-vote threshold is reached.

---

## 🚧 Known Limitations

- Admin CSS has minor styling issues on Render due to `django-cloudinary-storage` + Django 6.0 compatibility
- Azure Free tier (F1) has 60 CPU min/day limit — may slow under heavy load
- No email notifications for artifact approval/rejection

---

## 🔮 Future Enhancements

- **Skill Suggestion** — Allow users to propose new skills for admin review and approval
- Email notifications on artifact status change
- LinkedIn-style endorsements
- OAuth login (Google, GitHub)
- Skill categories and tags
- Public leaderboard
- Docker containerization
- Kubernetes deployment

---

## 👤 Author

**Thanmai** — [GitHub](https://github.com/Thanmai-11)

---

## 📄 License

This project is for educational purposes — Manipal Institute of Technology, Web Programming Lab (CSE 3243).
