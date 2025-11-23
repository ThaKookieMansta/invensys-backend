# InvenSys – Inventory & Asset Management System

A modern, containerized inventory and procurement management system built with FastAPI, PostgreSQL, SQLAlchemy (async),
MinIO, and Docker Compose.

## 🚀 Features

* FastAPI backend with fully async architecture

* PostgreSQL database

* MinIO object storage for uploaded documents (POs, receipts, etc.)

* Secure temporary download links

* Modular project structure (routes, schemas, CRUD, services)

## 🧱 Tech Stack

| Component   | Technology                       |
|-------------|----------------------------------|
| Backend API | FastAPI (Python 3.13)            |
| Database    | PostgreSQL 16                    |
| ORM         | SQLAlchemy 2.0 (async) + Alembic |
| Storage     | MinIO (S3-compatible)            |
| Auth        | JWT                              |
| Environment | .env driven configuration        |

## ⚙️ Environment Variables

Create a .env file in the root directory:

```dotenv
DB_VERSION=16
DB_CONTAINER_NAME=invensys-db
DB_USER=postgres
DB_PASSWORD=
DB_HOST=invensys-db
DB_PORT=5432
DB=invensys
SECRET_KEY=
MINIO_VERSION=latest
MINIO_CONTAINER_NAME=invensys-minio
MINIO_ENDPOINT=invensys-minio:9000
MINIO_ENDPOINT_API=9000
MINIO_CONSOLE_PORT=9001
MINIO_ROOT_USER=
MINIO_ROOT_PASSWORD=
MINIO_BUCKET=invensys
LOG_LEVEL=DEBUG


```

## 🧪 Running Locally Without Docker

```commandline
pip install -r requirements.txt
uvicorn app.main:app --reload

```

## 🛠️ Development Notes

* Uses async database queries (asyncpg)

* Uses presigned URLs for secure MinIO document downloads

* Includes automatic seeding via FastAPI lifespan

📄 License

MIT License
© 2025 InvenSys