from app.clients import transparencia
from app.schemas.cartoes import GastoCartao


async def listar_gastos(
    mes_ano_inicio: str,
    mes_ano_fim: str,
    pagina: int = 1,
    codigo_orgao: str | None = None,
    cpf_portador: str | None = None,
    cnpj_estabelecimento: str | None = None,
) -> list[GastoCartao]:
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

    data = await transparencia.get("/cartoes", params=params)
    return [GastoCartao(**item) for item in data]
