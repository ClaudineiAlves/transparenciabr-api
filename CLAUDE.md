# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

REST API that aggregates and exposes Brazilian government transparency data sourced from the [Portal da Transparência (CGU)](https://api.portaldatransparencia.gov.br/api-de-dados/). Built with FastAPI, PostgreSQL, and Alembic.

## Commands

```bash
# Run dev server
uvicorn app.main:app --reload

# Run tests
pytest

# Run a single test file
pytest tests/path/to/test_file.py

# Run a single test
pytest tests/path/to/test_file.py::test_function_name -v

# Migrations
alembic upgrade head
alembic revision --autogenerate -m "description"
alembic downgrade -1

# Lint / format
ruff check .
ruff format .
```

## Architecture

```
app/
  main.py          # FastAPI app factory, router registration, lifespan
  core/
    config.py      # Settings via pydantic-settings (reads .env)
    database.py    # Async SQLAlchemy engine and session factory
  api/
    v1/            # Versioned route handlers; one module per resource
  models/          # SQLAlchemy ORM models (table definitions)
  schemas/         # Pydantic schemas for request/response validation
  services/        # Business logic; orchestrates DB queries + external calls
  clients/
    transparencia.py  # Async HTTP client wrapping the Portal da Transparência API
alembic/
  versions/        # Auto-generated migration scripts
tests/
  conftest.py      # Fixtures: test DB session, async client, etc.
```

## Key Conventions

**Layering:** Routes call services; services call DB models and the `transparencia` client. Routes never query the DB directly and never call the external API directly.

**Async:** Use `async def` throughout. Database sessions use `AsyncSession`; HTTP calls use `httpx.AsyncClient`.

**Settings:** All config lives in `app/core/config.py` as a `Settings` class (pydantic-settings). Access via `from app.core.config import settings`. Never import `os.environ` directly elsewhere.

**Portal da Transparência client:** Base URL is `https://api.portaldatransparencia.gov.br/api-de-dados/`. Requires the `chave-api-dados` header with an API key from `settings.transparencia_api_key`. Rate limits apply — handle 429 with retry/backoff.

**Migrations:** Every model change requires an Alembic revision. Never edit the database schema manually.

**Tests:** Use `pytest-asyncio` with an in-memory or test-schema PostgreSQL DB (not SQLite). Mock external HTTP calls with `respx` or `pytest-httpx` — never hit the real Portal da Transparência in tests.
