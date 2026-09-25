import datetime as dt
from decimal import Decimal

from fastapi import Query

from app.services.armazenados import Filtros


def filtros_armazenados(
    codigo_orgao: str | None = Query(None, description="Código SIAFI do órgão"),
    data_de: dt.date | None = Query(
        None, description="Data inicial (AAAA-MM-DD)", examples=["2025-01-01"]
    ),
    data_ate: dt.date | None = Query(
        None, description="Data final (AAAA-MM-DD)", examples=["2025-01-31"]
    ),
    valor_min: Decimal | None = Query(None, ge=0, description="Valor mínimo (R$)"),
    valor_max: Decimal | None = Query(None, ge=0, description="Valor máximo (R$)"),
    pagina: int = Query(1, ge=1, description="Número da página"),
    tamanho: int = Query(50, ge=1, le=500, description="Registros por página"),
) -> Filtros:
    return Filtros(
        codigo_orgao=codigo_orgao,
        data_de=data_de,
        data_ate=data_ate,
        valor_min=valor_min,
        valor_max=valor_max,
        pagina=pagina,
        tamanho=tamanho,
    )
