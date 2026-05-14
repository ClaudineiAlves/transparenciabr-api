from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.core.exceptions import (
    PortalIndisponivel,
    handler_http_status,
    handler_portal_indisponivel,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Transparência BR API",
    description="API para dados do Portal da Transparência do Governo Federal.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_exception_handler(PortalIndisponivel, handler_portal_indisponivel)
app.add_exception_handler(httpx.HTTPStatusError, handler_http_status)

app.include_router(v1_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
