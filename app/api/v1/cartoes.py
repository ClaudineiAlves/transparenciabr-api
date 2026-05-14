from fastapi import APIRouter, Query

from app.schemas.cartoes import GastoCartao
from app.schemas.comum import Pagina
from app.services import cartoes as cartoes_service

router = APIRouter(prefix="/cartoes", tags=["Cartões Corporativos"])


@router.get("", response_model=Pagina[GastoCartao])
async def listar_gastos_cartao(
    mes_ano_inicio: str = Query(
        ..., description="Mês/ano inicial (MM/AAAA)", example="01/2025"
    ),
    mes_ano_fim: str = Query(
        ..., description="Mês/ano final (MM/AAAA)", example="03/2025"
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
    return await cartoes_service.listar_gastos(
        mes_ano_inicio=mes_ano_inicio,
        mes_ano_fim=mes_ano_fim,
        pagina=pagina,
        codigo_orgao=codigo_orgao,
        cpf_portador=cpf_portador,
        cnpj_estabelecimento=cnpj_estabelecimento,
    )
