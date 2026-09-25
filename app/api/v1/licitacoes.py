from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencias import filtros_armazenados
from app.core.database import get_db
from app.schemas.armazenados import LicitacaoArmazenada, PaginaArmazenada
from app.schemas.comum import Pagina
from app.schemas.licitacoes import Licitacao
from app.services import licitacoes as licitacoes_service
from app.services.armazenados import Filtros

router = APIRouter(prefix="/licitacoes", tags=["Licitações"])


@router.get("", response_model=Pagina[Licitacao])
async def listar_licitacoes(
    tarefas: BackgroundTasks,
    codigo_orgao: str = Query(..., description="Código SIAFI do órgão"),
    data_inicial: str = Query(
        ...,
        description="Data de abertura inicial (DD/MM/AAAA)",
        examples=["01/01/2025"],
    ),
    data_final: str = Query(
        ..., description="Data de abertura final (DD/MM/AAAA)", examples=["31/01/2025"]
    ),
    pagina: int = Query(1, ge=1, description="Número da página"),
):
    """Lista licitações realizadas pelo governo federal. Período máximo: 1 mês."""
    resultado = await licitacoes_service.listar_licitacoes(
        codigo_orgao=codigo_orgao,
        data_inicial=data_inicial,
        data_final=data_final,
        pagina=pagina,
    )
    tarefas.add_task(licitacoes_service.salvar, resultado.itens)
    return resultado


@router.get("/armazenados", response_model=PaginaArmazenada[LicitacaoArmazenada])
async def consultar_licitacoes_armazenadas(
    filtros: Filtros = Depends(filtros_armazenados),
    session: AsyncSession = Depends(get_db),
):
    """Consulta as licitações já gravadas, sem chamar o Portal.

    O período filtra a data de abertura e a faixa de valor, o valor da licitação.
    """
    return await licitacoes_service.consultar_armazenados(session, filtros)
