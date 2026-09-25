"""Acesso ao PostgreSQL: gravação idempotente e consulta dos registros do Portal."""

import datetime as dt
from collections.abc import Sequence
from decimal import Decimal
from typing import Any

from sqlalchemy import String, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from app.core.database import Base


def _cortar_textos(modelo: type[Base], registro: dict) -> dict:
    """Corta textos no tamanho da coluna, para um campo longo não derrubar o lote."""
    limites = {
        coluna.name: coluna.type.length
        for coluna in modelo.__table__.columns
        if isinstance(coluna.type, String) and coluna.type.length
    }
    return {
        campo: valor[: limites[campo]]
        if isinstance(valor, str) and campo in limites
        else valor
        for campo, valor in registro.items()
    }


async def salvar(
    session: AsyncSession, modelo: type[Base], registros: Sequence[dict]
) -> int:
    """Upsert por id: gravar a mesma página de novo atualiza em vez de duplicar."""
    # Um id repetido no mesmo INSERT quebraria o ON CONFLICT; o último vence.
    unicos = {r["id"]: _cortar_textos(modelo, r) for r in registros}
    if not unicos:
        return 0
    comando = insert(modelo).values(list(unicos.values()))
    atualizar = {
        coluna.name: comando.excluded[coluna.name]
        for coluna in modelo.__table__.columns
        if coluna.name not in ("id", "atualizado_em")
    }
    atualizar["atualizado_em"] = func.now()
    await session.execute(
        comando.on_conflict_do_update(index_elements=["id"], set_=atualizar)
    )
    await session.commit()
    return len(unicos)


async def consultar(
    session: AsyncSession,
    modelo: type[Base],
    *,
    coluna_data: InstrumentedAttribute,
    coluna_valor: InstrumentedAttribute,
    codigo_orgao: str | None = None,
    data_de: dt.date | None = None,
    data_ate: dt.date | None = None,
    valor_min: Decimal | None = None,
    valor_max: Decimal | None = None,
    pagina: int = 1,
    tamanho: int = 50,
) -> tuple[list[Any], int]:
    """Filtra por órgão, período e faixa de valor; devolve a página e o total."""
    filtros = []
    if codigo_orgao:
        filtros.append(modelo.orgao_codigo == codigo_orgao)
    if data_de:
        filtros.append(coluna_data >= data_de)
    if data_ate:
        filtros.append(coluna_data <= data_ate)
    if valor_min is not None:
        filtros.append(coluna_valor >= valor_min)
    if valor_max is not None:
        filtros.append(coluna_valor <= valor_max)

    total = await session.scalar(
        select(func.count()).select_from(modelo).where(*filtros)
    )
    consulta = (
        select(modelo)
        .where(*filtros)
        .order_by(coluna_data.desc().nulls_last(), modelo.id)
        .limit(tamanho)
        .offset((pagina - 1) * tamanho)
    )
    itens = (await session.scalars(consulta)).all()
    return list(itens), total or 0
