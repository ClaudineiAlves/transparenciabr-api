import logging
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

import app.models  # noqa: F401 — registers all models with Base.metadata
from app.api.v1.router import router as v1_router
from app.core import database
from app.core.exceptions import (
    BancoIndisponivel,
    ParametrosInvalidos,
    PortalIndisponivel,
    handler_banco_indisponivel,
    handler_http_status,
    handler_parametros_invalidos,
    handler_portal_indisponivel,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

_STATIC_INDEX = Path(__file__).parent.parent / "static" / "index.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App iniciado.")
    yield
    if database.engine is not None:
        await database.engine.dispose()


app = FastAPI(
    title="Transparência BR API",
    description="API para dados do Portal da Transparência do Governo Federal.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.add_exception_handler(PortalIndisponivel, handler_portal_indisponivel)
app.add_exception_handler(ParametrosInvalidos, handler_parametros_invalidos)
app.add_exception_handler(BancoIndisponivel, handler_banco_indisponivel)
app.add_exception_handler(httpx.HTTPStatusError, handler_http_status)

app.include_router(v1_router)


# HEAD também: monitores externos (UptimeRobot) checam com HEAD, e só GET dava 405
@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def frontend():
    return _STATIC_INDEX.read_text(encoding="utf-8")
