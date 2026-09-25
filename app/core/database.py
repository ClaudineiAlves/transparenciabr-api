from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
from app.core.exceptions import BancoIndisponivel

# pool_pre_ping: bancos serverless (Neon) encerram conexões ociosas.
engine = (
    create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
        connect_args={"timeout": 10},
    )
    if settings.database_url
    else None
)

AsyncSessionLocal = (
    async_sessionmaker(engine, expire_on_commit=False) if engine is not None else None
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if AsyncSessionLocal is None:
        raise BancoIndisponivel("DATABASE_URL não configurada")
    async with AsyncSessionLocal() as session:
        yield session
