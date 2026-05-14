import httpx

from app.core.config import settings

_BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"
_TIMEOUT = 30.0
_MAX_RETRIES = 3


def _build_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=_BASE_URL,
        headers={"chave-api-dados": settings.transparencia_api_key},
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
            response.raise_for_status()
            return response.json()
    response.raise_for_status()
