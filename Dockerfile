FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e "."

COPY . .

# Migrations no start (o plano free do Render não tem pre-deploy); se o banco
# falhar, a API sobe mesmo assim.
CMD ["sh", "-c", "(alembic upgrade head || alembic stamp head || true) && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
