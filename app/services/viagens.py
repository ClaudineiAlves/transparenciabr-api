import httpx

from app.clients import transparencia
from app.core.exceptions import PortalIndisponivel
from app.schemas.comum import Pagina
from app.schemas.viagens import Viagem


async def listar_viagens(
    codigo_orgao: str,
    data_ida_de: str,
    data_ida_ate: str,
    data_retorno_de: str,
    data_retorno_ate: str,
    pagina: int = 1,
) -> Pagina[Viagem]:
    params = {
        "codigoOrgao": codigo_orgao,
        "dataIdaDe": data_ida_de,
        "dataIdaAte": data_ida_ate,
        "dataRetornoDe": data_retorno_de,
        "dataRetornoAte": data_retorno_ate,
        "pagina": pagina,
    }

    try:
        data = await transparencia.get("/viagens", params=params)
    except httpx.HTTPStatusError as exc:
        raise PortalIndisponivel(str(exc.response.status_code)) from exc
    except httpx.RequestError as exc:
        raise PortalIndisponivel(str(exc)) from exc

    return Pagina(pagina=pagina, itens=[Viagem(**item) for item in data])
