from fastapi import APIRouter, Query

from app.schemas.comum import Pagina
from app.schemas.viagens import Viagem
from app.services import viagens as viagens_service

router = APIRouter(prefix="/viagens", tags=["Viagens a Serviço"])


@router.get("", response_model=Pagina[Viagem])
async def listar_viagens(
    codigo_orgao: str = Query(..., description="Código SIAFI do órgão"),
    data_ida_de: str = Query(
        ..., description="Data de ida inicial (DD/MM/AAAA)", examples=["01/01/2025"]
    ),
    data_ida_ate: str = Query(
        ..., description="Data de ida final (DD/MM/AAAA)", examples=["31/01/2025"]
    ),
    data_retorno_de: str = Query(
        ..., description="Data de retorno inicial (DD/MM/AAAA)", examples=["01/01/2025"]
    ),
    data_retorno_ate: str = Query(
        ..., description="Data de retorno final (DD/MM/AAAA)", examples=["31/01/2025"]
    ),
    pagina: int = Query(1, ge=1, description="Número da página"),
):
    """Lista viagens a serviço realizadas por servidores federais."""
    return await viagens_service.listar_viagens(
        codigo_orgao=codigo_orgao,
        data_ida_de=data_ida_de,
        data_ida_ate=data_ida_ate,
        data_retorno_de=data_retorno_de,
        data_retorno_ate=data_retorno_ate,
        pagina=pagina,
    )
