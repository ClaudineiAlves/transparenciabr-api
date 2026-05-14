from fastapi import APIRouter, Query

from app.schemas.comum import Pagina
from app.schemas.licitacoes import Licitacao
from app.services import licitacoes as licitacoes_service

router = APIRouter(prefix="/licitacoes", tags=["Licitações"])


@router.get("", response_model=Pagina[Licitacao])
async def listar_licitacoes(
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
    return await licitacoes_service.listar_licitacoes(
        codigo_orgao=codigo_orgao,
        data_inicial=data_inicial,
        data_final=data_final,
        pagina=pagina,
    )
