import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients import transparencia
from app.core.exceptions import PortalIndisponivel
from app.models.contrato import Contrato as ContratoModelo
from app.schemas.armazenados import ContratoArmazenado, PaginaArmazenada
from app.schemas.comum import Pagina
from app.schemas.contratos import Contrato
from app.services import armazenados, normalizacao, persistencia
from app.services.armazenados import Filtros


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


async def salvar(itens: list[Contrato]) -> None:
    await persistencia.salvar(ContratoModelo, itens, normalizacao.contrato)


async def consultar_armazenados(
    session: AsyncSession, filtros: Filtros
) -> PaginaArmazenada[ContratoArmazenado]:
    itens, total = await armazenados.consultar(
        session,
        ContratoModelo,
        ContratoModelo.data_assinatura,
        ContratoModelo.valor_final,
        filtros,
    )
    return PaginaArmazenada(
        pagina=filtros.pagina,
        tamanho=filtros.tamanho,
        total=total,
        itens=[ContratoArmazenado.model_validate(item) for item in itens],
    )
