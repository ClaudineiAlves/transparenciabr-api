import httpx
from fastapi import Request
from fastapi.responses import JSONResponse


class PortalIndisponivel(Exception):
    def __init__(self, detalhe: str):
        self.detalhe = detalhe


async def handler_portal_indisponivel(
    request: Request, exc: PortalIndisponivel
) -> JSONResponse:
    return JSONResponse(
        status_code=502,
        content={"mensagem": f"Portal da Transparência indisponível: {exc.detalhe}"},
    )


async def handler_http_status(
    request: Request, exc: httpx.HTTPStatusError
) -> JSONResponse:
    return JSONResponse(
        status_code=502,
        content={
            "mensagem": f"Erro ao consultar fonte externa: {exc.response.status_code}"
        },
    )
