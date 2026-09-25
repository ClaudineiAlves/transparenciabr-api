import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core import database
from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(autouse=True)
async def descartar_conexoes():
    # Cada teste roda num event loop novo e as conexões do asyncpg ficam presas ao
    # loop em que nasceram; reaproveitá-las no teste seguinte quebra.
    yield
    if database.engine is not None:
        await database.engine.dispose()


@pytest.fixture
async def banco():
    """Tabelas vazias e a fábrica de sessões. Sem PostgreSQL, o teste é pulado
    localmente; no CI (variável CI definida), a falta do banco é erro."""
    if database.engine is None:
        pytest.skip("DATABASE_URL não configurada")
    try:
        async with database.engine.begin() as conexao:
            await conexao.execute(
                text("TRUNCATE cartoes, contratos, licitacoes, viagens")
            )
    except (SQLAlchemyError, OSError) as exc:
        if os.getenv("CI"):
            raise
        pytest.skip(f"PostgreSQL indisponível: {exc}")
    return database.AsyncSessionLocal
