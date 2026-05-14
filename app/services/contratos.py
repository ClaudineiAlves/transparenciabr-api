import httpx

from app.clients import transparencia
from app.core.exceptions import PortalIndisponivel
from app.schemas.comum import Pagina
from app.schemas.contratos import Contrato


async def listar_contratos(
    codigo_orgao: str,
    data_inicio_de: str,
    data_inicio_ate: str,
    pagina: int = 1,
) -> Pagina[Contrato]:
    params = {
        "codigoOrgao": codigo_orgao,
        "dataInicioDe": data_inicio_de,
        "dataInicioAte": data_inicio_ate,
        "pagina": pagina,
    }

    try:
        data = await transparencia.get("/contratos", params=params)
    except httpx.HTTPStatusError as exc:
        raise PortalIndisponivel(str(exc.response.status_code)) from exc
    except httpx.RequestError as exc:
        raise PortalIndisponivel(str(exc)) from exc

    return Pagina(pagina=pagina, itens=[Contrato(**item) for item in data])
