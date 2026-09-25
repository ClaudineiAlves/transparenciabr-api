import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients import transparencia
from app.core.exceptions import PortalIndisponivel
from app.models.licitacao import Licitacao as LicitacaoModelo
from app.schemas.armazenados import LicitacaoArmazenada, PaginaArmazenada
from app.schemas.comum import Pagina
from app.schemas.licitacoes import Licitacao
from app.services import armazenados, normalizacao, persistencia
from app.services.armazenados import Filtros


async def listar_licitacoes(
    codigo_orgao: str,
    data_inicial: str,
    data_final: str,
    pagina: int = 1,
) -> Pagina[Licitacao]:
    params = {
        "codigoOrgao": codigo_orgao,
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "pagina": pagina,
    }

    try:
        data = await transparencia.get("/licitacoes", params=params)
    except httpx.HTTPStatusError as exc:
        raise PortalIndisponivel(str(exc.response.status_code)) from exc
    except httpx.RequestError as exc:
        raise PortalIndisponivel(str(exc)) from exc

    return Pagina(pagina=pagina, itens=[Licitacao(**item) for item in data])


async def salvar(itens: list[Licitacao]) -> None:
    await persistencia.salvar(LicitacaoModelo, itens, normalizacao.licitacao)


async def consultar_armazenados(
    session: AsyncSession, filtros: Filtros
) -> PaginaArmazenada[LicitacaoArmazenada]:
    itens, total = await armazenados.consultar(
        session,
        LicitacaoModelo,
        LicitacaoModelo.data_abertura,
        LicitacaoModelo.valor,
        filtros,
    )
    return PaginaArmazenada(
        pagina=filtros.pagina,
        tamanho=filtros.tamanho,
        total=total,
        itens=[LicitacaoArmazenada.model_validate(item) for item in itens],
    )
