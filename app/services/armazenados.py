"""Consulta dos registros já gravados, por órgão, período e faixa de valor."""

import datetime as dt
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from app.core.database import Base
from app.core.exceptions import BancoIndisponivel, ParametrosInvalidos
from app.repositories import registros


@dataclass(frozen=True)
class Filtros:
    codigo_orgao: str | None = None
    data_de: dt.date | None = None
    data_ate: dt.date | None = None
    valor_min: Decimal | None = None
    valor_max: Decimal | None = None
    pagina: int = 1
    tamanho: int = 50

    def validar(self) -> None:
        if self.data_de and self.data_ate and self.data_de > self.data_ate:
            raise ParametrosInvalidos("data_de é posterior a data_ate")
        if (
            self.valor_min is not None
            and self.valor_max is not None
            and self.valor_min > self.valor_max
        ):
            raise ParametrosInvalidos("valor_min é maior que valor_max")


async def consultar(
    session: AsyncSession,
    modelo: type[Base],
    coluna_data: InstrumentedAttribute,
    coluna_valor: InstrumentedAttribute,
    filtros: Filtros,
) -> tuple[list[Any], int]:
    filtros.validar()
    try:
        return await registros.consultar(
            session,
            modelo,
            coluna_data=coluna_data,
            coluna_valor=coluna_valor,
            codigo_orgao=filtros.codigo_orgao,
            data_de=filtros.data_de,
            data_ate=filtros.data_ate,
            valor_min=filtros.valor_min,
            valor_max=filtros.valor_max,
            pagina=filtros.pagina,
            tamanho=filtros.tamanho,
        )
    except (SQLAlchemyError, OSError, TimeoutError) as exc:
        raise BancoIndisponivel(str(exc)) from exc
