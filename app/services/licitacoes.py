import httpx

from app.clients import transparencia
from app.core.exceptions import PortalIndisponivel
from app.schemas.comum import Pagina
from app.schemas.licitacoes import Licitacao


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
