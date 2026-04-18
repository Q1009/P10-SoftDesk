# SoftDesk Support API

[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-green)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.17-red)](https://www.django-rest-framework.org/)

A REST API for tracking and reporting technical issues on IT applications.
Built with Django REST Framework, it provides project, issue, and comment management with a contributor-based permission system.

---

## Requirements

- Python 3.13+
- [Poetry](https://python-poetry.org/docs/#installation)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/quentintellier/p10-softdesk.git
cd p10-softdesk
```

### 2. Install dependencies

```bash
poetry install
```

### 3. Apply migrations

```bash
poetry run python manage.py migrate
```

### 4. (Optional) Load demo data

```bash
# First-time setup (idempotent)
poetry run python manage.py seed_data

# Full reset
poetry run python manage.py seed_data --reset
```

> Demo accounts password: `DemoPass2026!`

### 5. Start the server

```bash
poetry run python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/`.

---

## Authentication

The API uses **JWT (JSON Web Tokens)** via `djangorestframework-simplejwt`.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/token/` | Obtain an access token and a refresh token |
| POST | `/api/token/refresh/` | Refresh the access token |

**Example request:**

```json
POST /api/token/
{
    "username": "alice_martin",
    "password": "DemoPass2026!"
}
```

Include the token in all subsequent requests:

```
Authorization: Bearer <access_token>
```

---

## Endpoints

### Users

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | `/api/users/register/` | Create an account | No |
| GET | `/api/users/me/` | View own profile | Yes |
| PATCH | `/api/users/me/` | Update own profile | Yes |
| DELETE | `/api/users/me/` | Delete own account (right to erasure) | Yes |

**Required fields for registration:**

```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "password123",
    "date_of_birth": "1995-06-15",
    "can_be_contacted": true,
    "can_data_be_shared": false
}
```

> Minimum age is **15 years** (GDPR compliance).

---

### Projects

| Method | Endpoint | Description | Restriction |
|---|---|---|---|
| GET | `/api/projects/` | List projects | Authenticated |
| POST | `/api/projects/` | Create a project | Authenticated |
| GET | `/api/projects/{id}/` | Project detail | Contributor |
| PATCH | `/api/projects/{id}/` | Update a project | Author |
| DELETE | `/api/projects/{id}/` | Delete a project | Author |
| POST | `/api/projects/{id}/add-contributor/` | Add a contributor | Author |
| POST | `/api/projects/{id}/remove-contributor/` | Remove a contributor | Author |

**Required fields for creation:**

```json
{
    "name": "My project",
    "description": "Project description",
    "project_type": "BE"
}
```

> Project types: `BE` (Back-end), `FE` (Front-end), `IOS`, `AND` (Android)

**Add a contributor:**

```json
POST /api/projects/{id}/add-contributor/
{
    "user_id": 3,
    "contribution": "Developer"
}
```

---

### Issues

| Method | Endpoint | Description | Restriction |
|---|---|---|---|
| GET | `/api/projects/{project_pk}/issues/` | List issues | Contributor |
| POST | `/api/projects/{project_pk}/issues/` | Create an issue | Contributor |
| GET | `/api/projects/{project_pk}/issues/{id}/` | Issue detail | Contributor |
| PATCH | `/api/projects/{project_pk}/issues/{id}/` | Update an issue | Author |
| DELETE | `/api/projects/{project_pk}/issues/{id}/` | Delete an issue | Author |

**Required fields for creation:**

```json
{
    "title": "Issue title",
    "description": "Description",
    "assignee": 2
}
```

> `assignee` must be the `id` of a project contributor. The `project` and `author` fields are set automatically.

**Available fields for update (PATCH):**

| Field | Allowed values |
|---|---|
| `type` | `BUG`, `FEATURE`, `TASK` |
| `priority` | `LOW`, `MEDIUM`, `HIGH` |
| `status` | `TO_DO`, `IN_PROGRESS`, `FINISHED` |

---

### Comments

| Method | Endpoint | Description | Restriction |
|---|---|---|---|
| GET | `/api/projects/{project_pk}/issues/{issue_pk}/comments/` | List comments | Contributor |
| POST | `/api/projects/{project_pk}/issues/{issue_pk}/comments/` | Create a comment | Contributor |
| GET | `/api/projects/{project_pk}/issues/{issue_pk}/comments/{id}/` | Comment detail | Contributor |
| PATCH | `/api/projects/{project_pk}/issues/{issue_pk}/comments/{id}/` | Update a comment | Author |
| DELETE | `/api/projects/{project_pk}/issues/{issue_pk}/comments/{id}/` | Delete a comment | Author |

**Required fields for creation:**

```json
{
    "content": "Comment content"
}
```

> The `issue` and `author` fields are set automatically.

---

## Permissions

| Role | Rights |
|---|---|
| Unauthenticated | Registration only |
| Authenticated | Create a project, view own projects |
| Contributor | Read project resources, create issues and comments |
| Author | Edit and delete own resources, manage contributors |

---

## Pagination

Lists are paginated with **5 items per page** by default.

Available parameters: `limit` and `offset`.

```
GET /api/projects/?limit=10&offset=0
```

---

## Code Quality

PEP8 analysis with flake8:

```bash
poetry run flake8 --format=html --htmldir=flake8-report
```

The HTML report is generated in `flake8-report/index.html`.

