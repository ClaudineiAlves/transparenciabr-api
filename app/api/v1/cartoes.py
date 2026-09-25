from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencias import filtros_armazenados
from app.core.database import get_db
from app.schemas.armazenados import GastoCartaoArmazenado, PaginaArmazenada
from app.schemas.cartoes import GastoCartao
from app.schemas.comum import Pagina
from app.services import cartoes as cartoes_service
from app.services.armazenados import Filtros

router = APIRouter(prefix="/cartoes", tags=["Cartões Corporativos"])


@router.get("", response_model=Pagina[GastoCartao])
async def listar_gastos_cartao(
    tarefas: BackgroundTasks,
    mes_ano_inicio: str = Query(
        ...,
        description="Mês/ano inicial (MM/AAAA)",
        examples=["01/2025"],
    ),
    mes_ano_fim: str = Query(
        ..., description="Mês/ano final (MM/AAAA)", examples=["03/2025"]
    ),
    pagina: int = Query(1, ge=1, description="Número da página"),
    codigo_orgao: str | None = Query(None, description="Código SIAFI do órgão"),
    cpf_portador: str | None = Query(
        None, description="CPF do portador (sem pontuação)"
    ),
    cnpj_estabelecimento: str | None = Query(
        None, description="CNPJ do estabelecimento (sem pontuação)"
    ),
):
    """
    Lista gastos realizados com cartões corporativos do governo federal.

    Requer ao menos um dos filtros opcionais (órgão, portador ou estabelecimento),
    ou um período de até 12 meses.
    """
    resultado = await cartoes_service.listar_gastos(
        mes_ano_inicio=mes_ano_inicio,
        mes_ano_fim=mes_ano_fim,
        pagina=pagina,
        codigo_orgao=codigo_orgao,
        cpf_portador=cpf_portador,
        cnpj_estabelecimento=cnpj_estabelecimento,
    )
    tarefas.add_task(cartoes_service.salvar, resultado.itens)
    return resultado


@router.get("/armazenados", response_model=PaginaArmazenada[GastoCartaoArmazenado])
async def consultar_gastos_armazenados(
    filtros: Filtros = Depends(filtros_armazenados),
    session: AsyncSession = Depends(get_db),
):
    """Consulta os gastos já gravados, sem chamar o Portal.

    O período filtra a data da transação e a faixa de valor, o valor da transação.
    """
    return await cartoes_service.consultar_armazenados(session, filtros)
