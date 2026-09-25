from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencias import filtros_armazenados
from app.core.database import get_db
from app.schemas.armazenados import ContratoArmazenado, PaginaArmazenada
from app.schemas.comum import Pagina
from app.schemas.contratos import Contrato
from app.services import contratos as contratos_service
from app.services.armazenados import Filtros

router = APIRouter(prefix="/contratos", tags=["Contratos"])


@router.get("", response_model=Pagina[Contrato])
async def listar_contratos(
    tarefas: BackgroundTasks,
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
    resultado = await contratos_service.listar_contratos(
        codigo_orgao=codigo_orgao,
        data_inicio_de=data_inicio_de,
        data_inicio_ate=data_inicio_ate,
        pagina=pagina,
    )
    tarefas.add_task(contratos_service.salvar, resultado.itens)
    return resultado


@router.get("/armazenados", response_model=PaginaArmazenada[ContratoArmazenado])
async def consultar_contratos_armazenados(
    filtros: Filtros = Depends(filtros_armazenados),
    session: AsyncSession = Depends(get_db),
):
    """Consulta os contratos já gravados, sem chamar o Portal.

    O período filtra a data de assinatura e a faixa de valor, o valor final.
    """
    return await contratos_service.consultar_armazenados(session, filtros)
