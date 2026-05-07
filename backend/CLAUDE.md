# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development commands

```bash
# Run the dev server
python main.py

# Run with custom env vars
env=prod python main.py

# Run Alembic migrations
alembic upgrade head                  # apply all pending migrations
alembic revision --autogenerate -m "description"  # create new migration
alembic history                       # view migration history
alembic downgrade -1                  # rollback one migration

# Production (Gunicorn + UvicornWorker, 4 workers)
gunicorn main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000

# Docker build & run
docker build -t journal-backend .
docker run -p 8000:8000 --env-file .env journal-backend

# Sync dependencies (uv, not pip)
uv sync
```

## Architecture overview

**Stack**: FastAPI + SQLAlchemy 2.0 async (asyncpg) + PostgreSQL + Redis + Kafka + Elasticsearch

**Layer flow**: `api/v1/` (routers) → `service/` (business logic) → `database/repositories/` (data access) → `database/orm/models/` (SQLAlchemy models). Pydantic DTOs live in `model/`.

### Service lifecycle

Third-party services (DB, Redis, Kafka, ES, Email, Payment) inherit `BaseManagedService` from `core/service_manager.py`. The constructor auto-registers each service with the singleton `ServiceManager`. On app startup (`lifespan` in `main.py`), `service_manager.start_all()` launches services in two tiers:

- **Critical** (failure → app abort): `database`, `redis`
- **Optional** (failure → warning only): `kafka`, `elasticsearch`, `email`, `payment`

Each service must implement `async start()` and `async stop()`.

### Config system

TOML files in `configs/` are loaded by the `Config` singleton (`core/config.py`). Access with dot-path notation:

```python
config["global.global.env"]           # exact lookup, raises KeyError if missing
config.get("global.global.env", "dev") # safe lookup with default
config.get_table("database")          # returns entire TOML table as dict
```

Secrets (`${VAR_NAME}` placeholders in TOML) are resolved from environment variables. Production mode (`env = "prod"`) validates that no unresolved placeholders remain.

### Authentication flow

1. Client SHA256 hashes plaintext password, sends hash to server
2. Server applies salt: `SHA256(salt + client_sha256)`, truncates to 72 bytes
3. Result is bcrypt-hashed for storage / verification
4. JWT tokens signed with HS256 key stored in Redis (supports key rotation — current + previous key)
5. On login, token → user mapping stored in Redis with TTL
6. `get_current_user` dependency (in `api/dependencies/security.py`) validates: Redis session → JWT verify → DB user lookup → refresh Redis TTL

### Role hierarchy

Defined in `core/enums.py` as `UserRole`: `admin (6) > editor (5) > associate_editor (4) > ea_ae (3) > reviewer (2) > author (1) > user (0)`. Use `UserRole.has_permission(current_role, required_role)` for permission checks. Specialized FastAPI dependencies for each role level are in `api/dependencies/security.py`.

### Manuscript workflow

`ManuscriptStatus` (25 states) grouped by `ReviewStage`: `initial_review` → `peer_review` → `final_decision` → publication. State transitions are driven by `WorkflowAction` enum values through the manuscript workflow endpoint.

### Database layer

- **ORM Base**: `database/orm/base.py` — all models inherit `Base`
- **Session factory**: `database/orm/session.py` — builds async Engine + sessionmaker from `database.toml`
- **Repository pattern**: `database/repositories/base_repo.py` (`BaseRepository[T]`) provides `get_by_id`, `count`, `list_page`, `list_page_as_dict`, `add`
- **Unit of work**: `database/uow.py` provides `transactional(session)` context manager
- **DI**: Use `get_db_session` from `database/dependencies.py` in route handlers

### API response format

All endpoints return `{code, message, data, meta}` via `model/response.py` (`ApiResponse`). Use class methods `ApiResponse.success()`, `ApiResponse.error()`, `ApiResponse.paginated()`.

### Key files to know

- `main.py` — app creation, lifespan, route registration
- `core/config.py` — Config singleton + `setup_core()` (CORS, error handlers)
- `core/service_manager.py` — `BaseManagedService` + `ServiceManager`
- `api/v1/__init__.py` — all v1 sub-routers assembled under `/api/v1` prefix
- `api/dependencies/security.py` — auth dependencies (`get_current_user`, `require_role`, etc.)
- `database/service/database_service.py` — `DatabaseManager` (Engine + session lifecycle)
- `utils/jwt.py` — JWT create/verify + bcrypt password hashing
- `utils/log.py` — `global_logger` based on loguru (configured after config loads)
