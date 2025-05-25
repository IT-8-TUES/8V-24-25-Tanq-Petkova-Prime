# TanqTasks

A lean, layered **task management platform** for individuals and teams. Organize work by **firms**, assign and track **tasks**, and collaborate seamlessly.

---

## Project Overview

TanqTasks allows firm owners to create **firms** (teams), invite users, and assign tasks. Users can accept invites, view their tasks, and track progress in a clean, intuitive UI.

Both frontend (static HTML/JS) and backend (Django REST API) run locally:

* **Frontend:** `http://localhost:9000`
* **Backend:** `http://localhost:8000`

---

## Features

* **Firm Management:** Create, edit, and delete firms
* **User Invites:** Invite and remove members
* **Task Assignment:** Owners assign tasks to members
* **Task Tracking:** Users view, edit, and delete their tasks
* **Authentication:** Secure API calls via `fetchWithAuth` (ES module)

---

## Getting Started

### 1. Frontend

```bash
cd 8V-24-25-Tanq-Petkova-Prime/frontend
# Serve at localhost:9000 for ES module imports
python3 -m http.server 9000
```

### 2. Backend

```bash
cd 8V-24-25-Tanq-Petkova-Prime/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 3. Open the App

* Frontend: `http://localhost:9000/Misho/heropage.html`

---

## Directory Structure

```
8V-24-25-Tanq-Petkova-Prime/
├── frontend/
│   ├── ivan/
│   ├── Marto/
│   └── Misho/
│       └── heropage.html
└── backend/
    ├── requirements.txt
    └── (Django project files)
```

---

## Architecture

**Frontend**: Vanilla HTML/CSS/JS with ES modules for auth

**Backend**: Django REST Framework, endpoints for firms, tasks, invites, memberships, and image uploads
