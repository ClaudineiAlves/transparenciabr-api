FROM python:3.11-slim

WORKDIR /app

# Versões travadas em requirements.txt (gerado do pyproject.toml pelo uv); o pacote
# em si entra sem dependências para não resolver nada de novo no build
COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --no-deps -e "."

COPY . .

# Migrations no start (o plano free do Render não tem pre-deploy); se o banco
# falhar, a API sobe mesmo assim e só a gravação e o /armazenados ficam fora. Sem
# "alembic stamp head": marcar como aplicada uma migration que falhou faria a API
# gravar num schema velho sem avisar.
CMD ["sh", "-c", "(alembic upgrade head || echo 'alembic upgrade head falhou') && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
