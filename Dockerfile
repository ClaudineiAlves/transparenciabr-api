FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

COPY . .

CMD ["sh", "-c", "echo '=== running alembic ===' && alembic upgrade head; echo '=== alembic exit '$?' ===' && echo '=== starting uvicorn on port '${PORT:-8000}' ===' && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
