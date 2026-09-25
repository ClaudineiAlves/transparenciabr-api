import pytest

from app.core.config import Settings


@pytest.mark.parametrize(
    ("url", "esperada"),
    [
        (
            "postgres://u:senha@host:5432/db",
            "postgresql+asyncpg://u:senha@host:5432/db",
        ),
        (
            "postgresql://u:senha@host/db?sslmode=require&channel_binding=require",
            "postgresql+asyncpg://u:senha@host/db?ssl=require",
        ),
        (
            "postgresql+asyncpg://u:senha@localhost:5432/db",
            "postgresql+asyncpg://u:senha@localhost:5432/db",
        ),
        ("", None),
        (None, None),
    ],
)
def test_database_url_normalizada_para_o_asyncpg(url, esperada):
    settings = Settings(database_url=url, transparencia_api_key="x")

    assert settings.database_url == esperada
