import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients import transparencia
from app.core.exceptions import PortalIndisponivel
from app.models.cartao import Cartao
from app.schemas.armazenados import GastoCartaoArmazenado, PaginaArmazenada
from app.schemas.cartoes import GastoCartao
from app.schemas.comum import Pagina
from app.services import armazenados, normalizacao, persistencia
from app.services.armazenados import Filtros


async def listar_gastos(
    mes_ano_inicio: str,
    mes_ano_fim: str,
    pagina: int = 1,
    codigo_orgao: str | None = None,
    cpf_portador: str | None = None,
    cnpj_estabelecimento: str | None = None,
) -> Pagina[GastoCartao]:
    params = {
        "mesAnoInicio": mes_ano_inicio,
        "mesAnoFim": mes_ano_fim,
        "pagina": pagina,
    }
    if codigo_orgao:
        params["codigoOrgao"] = codigo_orgao
    if cpf_portador:
        params["cpfPortador"] = cpf_portador
    if cnpj_estabelecimento:
        params["cnpjEstabelecimento"] = cnpj_estabelecimento

    try:
        data = await transparencia.get("/cartoes", params=params)
    except httpx.HTTPStatusError as exc:
        raise PortalIndisponivel(str(exc.response.status_code)) from exc
    except httpx.RequestError as exc:
        raise PortalIndisponivel(str(exc)) from exc

    return Pagina(pagina=pagina, itens=[GastoCartao(**item) for item in data])


async def salvar(itens: list[GastoCartao]) -> None:
    await persistencia.salvar(Cartao, itens, normalizacao.cartao)


async def consultar_armazenados(
    session: AsyncSession, filtros: Filtros
) -> PaginaArmazenada[GastoCartaoArmazenado]:
    itens, total = await armazenados.consultar(
        session, Cartao, Cartao.data_transacao, Cartao.valor_transacao, filtros
    )
    return PaginaArmazenada(
        pagina=filtros.pagina,
        tamanho=filtros.tamanho,
        total=total,
        itens=[GastoCartaoArmazenado.model_validate(item) for item in itens],
    )
