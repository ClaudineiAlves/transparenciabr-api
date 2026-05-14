from fastapi import APIRouter, Query

from app.schemas.comum import Pagina
from app.schemas.contratos import Contrato
from app.services import contratos as contratos_service

router = APIRouter(prefix="/contratos", tags=["Contratos"])


@router.get("", response_model=Pagina[Contrato])
async def listar_contratos(
    codigo_orgao: str = Query(..., description="Código SIAFI do órgão"),
    data_inicio_de: str = Query(
        ..., description="Data de início inicial (DD/MM/AAAA)", examples=["01/01/2025"]
    ),
    data_inicio_ate: str = Query(
        ..., description="Data de início final (DD/MM/AAAA)", examples=["31/01/2025"]
    ),
    pagina: int = Query(1, ge=1, description="Número da página"),
):
    """Lista contratos celebrados pelo governo federal."""
    return await contratos_service.listar_contratos(
        codigo_orgao=codigo_orgao,
        data_inicio_de=data_inicio_de,
        data_inicio_ate=data_inicio_ate,
        pagina=pagina,
    )
