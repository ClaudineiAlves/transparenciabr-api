import httpx

from app.core.config import settings
from app.core.exceptions import ParametrosInvalidos

_BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"
_TIMEOUT = 30.0
_MAX_RETRIES = 3


def _build_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=_BASE_URL,
        headers={
            "chave-api-dados": settings.transparencia_api_key,
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-BR,pt;q=0.9",
        },
        timeout=_TIMEOUT,
    )


async def get(path: str, params: dict | None = None) -> dict | list:
    """
    GET against the Portal da Transparência API with basic retry on 429.
    Raises httpx.HTTPStatusError for non-2xx responses after retries.
    """
    async with _build_client() as client:
        for attempt in range(_MAX_RETRIES):
            response = await client.get(path, params=params)
            if response.status_code == 429 and attempt < _MAX_RETRIES - 1:
                import asyncio

                retry_after = int(response.headers.get("Retry-After", 5))
                await asyncio.sleep(retry_after)
                continue
            if response.status_code == 400:
                try:
                    detail = response.json()
                    msg = (
                        next(iter(detail.values()))
                        if isinstance(detail, dict)
                        else str(detail)
                    )
                except Exception:
                    msg = response.text
                raise ParametrosInvalidos(msg)
            response.raise_for_status()
            return response.json()
    response.raise_for_status()
