
# 🚀 Algorithmic Dev Backend

High-performance, modular backend API built with **FastAPI**, designed for scalability and maintainability.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis)
![Docker](https://img.shields.io/badge/Docker-25-2496ED?style=for-the-badge&logo=docker)

## 🛠 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - High performance, easy to learn, fast to code, ready for production.
- **Database**: [PostgreSQL](https://www.postgresql.org/) - The World's Most Advanced Open Source Relational Database.
- **ORM**: [SQLModel](https://sqlmodel.tiangolo.com/) - SQL databases in Python, designed for simplicity, compatibility, and robustness.
- **Caching**: [Redis](https://redis.io/) - In-memory data store for caching and pub/sub.
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/) - A database migration tool for SQLAlchemy.
- **Validation**: [Pydantic](https://docs.pydantic.dev/) - Data validation using Python type hints.
- **Containerization**: [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) - Local development and deployment.
- **Package Management**: [uv](https://github.com/astral-sh/uv) - An extremely fast Python package installer and resolver.

## ✨ Key Features

- **🔐 Robust Authentication & Authorization**
  - JWT-based authentication.
  - Role-Based Access Control (RBAC) with granular permissions.
  - Secure session management

- **📚 Education Module**
  - **Tutorials**: Create and manage comprehensive tutorials.
  - **Hierarchical Nodes**: Recursive structure for chapters and topics (Any depth support).

- **💼 Job Portal**
  - Job posting and management system.
  - Integration with user applications.

- **👥 User Management**
  - Profile management.
  - Secure password handling (Bcrypt).

- **⚙️ Advanced System Architecture**
  - **Modular Design**: Domain-driven directory structure (`app/modules/`).
  - **Global Error Handling**: Centralized exception handlers.
  - **Health Checks**: Ready for load balancer integration (`/health`).
  - **Hot Reloading**: Optimized Docker setup for rapid local development.

## 📂 Project Structure

```bash
backend/
├── app/
│   ├── common/             # Shared utilities, DB config, caching, exceptions
│   ├── config/             # App configuration (settings, router)
│   ├── modules/            # Domain-specific modules (DDD approach)
│   │   ├── auth/           # Authentication logic
│   │   ├── education/      # Tutorials and learning content
│   │   ├── jobs/           # Job board functionality
│   │   └── users/          # User management
│   ├── app.py              # Application entry point
│   └── server.py           # Uvicorn server config
├── alembic/                # Database migrations
├── docker-compose.dev.yml  # Local development infrastructure
├── pyproject.toml          # Dependencies and tool config
└── Makefile                # Handy commands
```

## 🚀 Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.

### Installation

1.  **Clone the repository**
    ```bash
    git clone <repository_url>
    cd backend
    ```

2.  **Environment Setup**
    ```bash
    cp .env.example .env
    # Update .env with your local credentials if needed
    ```

3.  **Run with Docker (Recommended)**
    Start the backend, postgres, and redis containers.
    ```bash
    docker compose -f docker-compose.dev.yml up --build
    ```

4.  **Access the API**
    - API Documentation: [http://localhost:4001/docs](http://localhost:4001/docs)
    - Health Check: [http://localhost:4001/health](http://localhost:4001/health)

## 🧪 Development

- **Run Migrations**:
  The Docker setup is configured to run migrations automatically on startup (`RUN_MIGRATIONS=true` in `docker-compose.dev.yml`).

- **Create Migration**:
  ```bash
  make docker_alembic_revision MSG="your migration message"
  ```

- **Apply Migration**:
  ```bash
  make docker_alembic_upgrade
  ```
