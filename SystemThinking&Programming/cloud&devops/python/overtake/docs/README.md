# Overtake — Multi-User Multimedia Note-Taking API

> A fully-functional, single-file FastAPI backend for multi-user multimedia note-taking, backed by AWS RDS PostgreSQL + S3 (via Terraform + LocalStack).

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Reference](#api-reference)
  - [Authentication](#authentication)
  - [Notes](#notes)
  - [Attachments](#attachments)
  - [Health](#health)
- [Database Schema](#database-schema)
- [Infrastructure (Terraform)](#infrastructure-terraform)
- [Makefile Targets](#makefile-targets)
- [Postman Testing Guide](#postman-testing-guide)
- [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
┌──────────────┐      ┌──────────────────┐      ┌───────────────────┐
│   Client     │      │   FastAPI App     │      │   LocalStack      │
│  (Postman /  │─────▶│   (main.py)       │─────▶│                   │
│   curl)      │      │                   │      │  ┌─────────────┐  │
│              │◀─────│  JWT Auth         │      │  │ RDS Postgres│  │
│              │      │  SQLModel ORM     │─────▶│  │  (Port 4510)│  │
│              │      │  S3 Client        │      │  └─────────────┘  │
│              │      │                   │      │  ┌─────────────┐  │
│              │      │                   │─────▶│  │ S3 Bucket   │  │
│              │      │                   │      │  │ overtake-   │  │
│              │      │                   │      │  │ media       │  │
└──────────────┘      └──────────────────┘      │  └─────────────┘  │
                                                 └───────────────────┘
```

---

## Tech Stack

| Layer             | Technology                          |
|-------------------|-------------------------------------|
| **Framework**     | FastAPI                             |
| **ORM**           | SQLModel (SQLAlchemy + Pydantic)    |
| **Database**      | PostgreSQL via AWS RDS (LocalStack) |
| **File Storage**  | AWS S3 (LocalStack)                 |
| **Auth**          | JWT (python-jose) + bcrypt          |
| **IaC**           | Terraform                           |
| **Local Cloud**   | LocalStack                          |
| **Pkg Manager**   | Poetry (pyproject.toml)             |
| **Env Manager**   | uv (fast venv + pip)                |
| **Task Runner**   | GNU Make                            |

---

## Project Structure

```
overtake/
├── main.py              # Entire FastAPI backend (single file, ~700 lines)
├── pyproject.toml       # Poetry project definition + dependencies
├── .env                 # Environment configuration
├── Makefile             # Dev workflow commands
├── docker-compose.yml   # LocalStack container (optional)
├── docs/
│   └── README.md        # This documentation
└── terraform/
    ├── providers.tf     # AWS provider → LocalStack
    └── main.tf          # RDS PostgreSQL + S3 bucket resources
```

---

## Prerequisites

| Tool       | Install Command           | Purpose                    |
|------------|---------------------------|----------------------------|
| Python     | `>=3.11`                  | Runtime                    |
| Docker     | Desktop or CLI            | LocalStack container       |
| LocalStack | `pip install localstack`  | AWS simulator              |
| uv         | `scoop install uv`        | Fast venv + package install|
| Make       | `scoop install make`      | Task runner                |
| Terraform  | `scoop install terraform` | Infrastructure as Code     |

---

## Quick Start

```bash
# 1. Create virtual environment
make venv

# 2. Install all dependencies
make install

# 3. Start LocalStack
localstack start      # in a separate terminal

# 4. Provision infrastructure (RDS + S3)
make infra-up

# 5. Run the API server
make run
```

The API is now live at **http://localhost:8000**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Configuration

All configuration is in `.env`:

```env
# AWS / LocalStack
AWS_ENDPOINT_URL=http://localhost:4566
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
S3_BUCKET_NAME=overtake-media

# Database (RDS PostgreSQL)
DATABASE_URL=postgresql://overtake:overtake123@localhost.localstack.cloud:4510/overtake_db

# JWT Authentication
JWT_SECRET_KEY=super-secret-change-me-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## API Reference

### Authentication

#### Register a New User

```
POST /auth/register
Content-Type: application/json

{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepass123"
}
```

**Response** `201 Created`:
```json
{
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2026-03-05T21:10:23.920639"
}
```

**Errors**: `409 Conflict` (username/email taken)

---

#### Login (Get JWT Token)

```
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=securepass123
```

**Response** `200 OK`:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

**Errors**: `401 Unauthorized` (invalid credentials)

> **Usage**: Include the token in all subsequent requests:
> ```
> Authorization: Bearer <access_token>
> ```

---

#### Get Current User

```
GET /auth/me
Authorization: Bearer <token>
```

**Response** `200 OK`:
```json
{
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2026-03-05T21:10:23.920639"
}
```

---

### Notes

> **All note endpoints require `Authorization: Bearer <token>` header.**
> Users can only access their own notes (multi-user isolation enforced).

#### Create a Note

```
POST /notes
Authorization: Bearer <token>
Content-Type: application/json

{
    "title": "Meeting Notes",
    "content": "Discussed Q3 roadmap and quarterly targets",
    "is_pinned": false
}
```

**Response** `201 Created`:
```json
{
    "id": 1,
    "title": "Meeting Notes",
    "content": "Discussed Q3 roadmap and quarterly targets",
    "is_pinned": false,
    "created_at": "2026-03-05T21:11:40.889286",
    "updated_at": "2026-03-05T21:11:40.889301",
    "attachments": []
}
```

---

#### List Notes (with Search & Pagination)

```
GET /notes?search=meeting&is_pinned=true&page=1&page_size=20
Authorization: Bearer <token>
```

**Query Parameters**:

| Param       | Type   | Default | Description                  |
|-------------|--------|---------|------------------------------|
| `search`    | string | null    | Search in title and content  |
| `is_pinned` | bool   | null    | Filter pinned/unpinned notes |
| `page`      | int    | 1       | Page number (1-indexed)      |
| `page_size` | int    | 20      | Results per page (1-100)     |

**Response** `200 OK`:
```json
{
    "notes": [...],
    "total": 5,
    "page": 1,
    "page_size": 20
}
```

---

#### Get a Note

```
GET /notes/{note_id}
Authorization: Bearer <token>
```

**Response** `200 OK`: Full note with attachments list.
**Errors**: `404 Not Found` (not yours or doesn't exist)

---

#### Update a Note

```
PUT /notes/{note_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "title": "Updated Title",
    "content": "Updated content",
    "is_pinned": true
}
```

All fields are optional — send only what you want to change.

---

#### Delete a Note

```
DELETE /notes/{note_id}
Authorization: Bearer <token>
```

**Response** `204 No Content`

> **Cascade**: Deleting a note also deletes all its attachments (both DB records and S3 objects).

---

### Attachments

#### Upload a File

```
POST /notes/{note_id}/attachments
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary file data>
```

**Response** `201 Created`:
```json
{
    "id": 1,
    "filename": "meeting_photo.jpg",
    "content_type": "image/jpeg",
    "size_bytes": 245760,
    "uploaded_at": "2026-03-05T21:12:14.429851"
}
```

Supported file types: **any** (images, PDFs, audio, video, documents, etc.)

Files are stored in S3 under the path: `users/{user_id}/notes/{note_id}/{uuid}.{ext}`

---

#### List Attachments

```
GET /notes/{note_id}/attachments
Authorization: Bearer <token>
```

**Response** `200 OK`: Array of attachment metadata.

---

#### Download a File

```
GET /attachments/{attachment_id}/download
Authorization: Bearer <token>
```

**Response**: Binary file stream with correct `Content-Type` and `Content-Disposition` headers.

---

#### Delete an Attachment

```
DELETE /attachments/{attachment_id}
Authorization: Bearer <token>
```

**Response** `204 No Content` (removes from both S3 and DB)

---

### Health

```
GET /health
```

**Response** `200 OK`:
```json
{
    "status": "ok",
    "service": "overtake",
    "version": "0.1.0"
}
```

---

## Database Schema

```
┌────────────────┐       ┌──────────────────┐       ┌────────────────────┐
│     users      │       │      notes       │       │   attachments      │
├────────────────┤       ├──────────────────┤       ├────────────────────┤
│ id (PK)        │──┐    │ id (PK)          │──┐    │ id (PK)            │
│ username (UQ)  │  │    │ title            │  │    │ filename           │
│ email (UQ)     │  │    │ content          │  │    │ s3_key             │
│ hashed_password│  └───▶│ user_id (FK)     │  └───▶│ note_id (FK)       │
│ created_at     │       │ is_pinned        │       │ content_type       │
│                │       │ created_at       │       │ size_bytes         │
│                │       │ updated_at       │       │ uploaded_at        │
└────────────────┘       └──────────────────┘       └────────────────────┘
```

**Relationships**:
- `User` → `Note`: One-to-Many (cascade delete)
- `Note` → `Attachment`: One-to-Many (cascade delete)

---

## Infrastructure (Terraform)

### Resources Provisioned

| Resource          | Name           | Details                           |
|-------------------|----------------|-----------------------------------|
| `aws_db_instance` | `overtake-db`  | PostgreSQL 16.1, port 4510        |
| `aws_s3_bucket`   | `overtake-media` | Force-destroy enabled            |

### Terraform Commands

```bash
# Initialize (downloads AWS provider)
cd terraform && terraform init

# Apply (creates RDS + S3)
terraform apply -auto-approve

# Destroy (removes all resources)
terraform destroy -auto-approve
```

### Provider Configuration

The AWS provider targets LocalStack with:
- Endpoint: `http://localhost:4566`
- Credentials: `test` / `test`
- `s3_use_path_style = true` (required for LocalStack)

---

## Makefile Targets

| Target       | Command               | Description                          |
|--------------|-----------------------|--------------------------------------|
| `make help`  |                       | Show all available targets           |
| `make venv`  | `uv venv .venv`       | Create Python virtual environment    |
| `make install`|                      | Install all dependencies via uv      |
| `make infra-up`|                     | Terraform init + apply               |
| `make infra-down`|                   | Terraform destroy                    |
| `make run`   | `uvicorn main:app`    | Start dev server on `:8000`          |
| `make fmt`   | `ruff format + check` | Format and lint code                 |
| `make clean` |                       | Remove venv, caches, terraform state |

---

## Postman Testing Guide

### Setup

1. Start the server: `make run`
2. Open Postman or use the Swagger UI at `http://localhost:8000/docs`

### Test Flow

```
1. POST /auth/register      → Create account
2. POST /auth/login          → Get JWT token
3. Set "Authorization: Bearer <token>" header for all subsequent requests
4. POST /notes               → Create a note
5. POST /notes/1/attachments → Upload a file (use form-data, key: "file")
6. GET  /notes               → List your notes
7. GET  /notes/1             → Get note with attachment details
8. GET  /attachments/1/download → Download the uploaded file
9. PUT  /notes/1             → Update the note
10. DELETE /attachments/1    → Delete the attachment
11. DELETE /notes/1          → Delete the note (cascades)
```

### Multi-User Isolation Test

```
1. Register User A, login, create a note
2. Register User B, login
3. GET /notes → User B sees empty list
4. GET /notes/1 → User B gets 404 (cannot access User A's note)
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `make` not found | `scoop install make` |
| `uv` not found | `scoop install uv` |
| `terraform` not found | `scoop install terraform` |
| S3 "no such host" error | Add `s3_use_path_style = true` to provider |
| Unicode emoji crash on Windows | Use ASCII-only in print statements |
| passlib bcrypt error on Python 3.13 | Use `bcrypt` directly (already done) |
| Port 8000 in use | Kill existing process or change port in Makefile |
| RDS connection refused | Ensure LocalStack is running: `localstack start` |
