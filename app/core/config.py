from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Opcional: sem banco, a API continua servindo o Portal; só não grava nem
    # atende as consultas em /armazenados.
    database_url: str | None = None
    transparencia_api_key: str

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_database_url(cls, v: str | None) -> str | None:
        if not v:
            return None
        url = make_url(v)
        if url.drivername in ("postgres", "postgresql"):
            url = url.set(drivername="postgresql+asyncpg")
        # Neon, Render e Supabase entregam a URL com os parâmetros de SSL do libpq,
        # que o asyncpg não reconhece.
        query = dict(url.query)
        if "sslmode" in query:
            query["ssl"] = query.pop("sslmode")
        query.pop("channel_binding", None)
        return url.set(query=query).render_as_string(hide_password=False)


settings = Settings()
