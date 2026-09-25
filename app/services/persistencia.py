"""Grava em background as páginas vindas do Portal; banco fora não derruba a API."""

import logging
from collections.abc import Callable, Sequence
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from app.core import database
from app.repositories import registros

logger = logging.getLogger(__name__)


async def salvar(
    modelo: type[database.Base],
    itens: Sequence[Any],
    normalizar: Callable[[Any], dict],
) -> None:
    if database.AsyncSessionLocal is None or not itens:
        return
    try:
        async with database.AsyncSessionLocal() as session:
            gravados = await registros.salvar(
                session, modelo, [normalizar(item) for item in itens]
            )
        logger.info("%d registros gravados em %s", gravados, modelo.__tablename__)
    except (SQLAlchemyError, OSError, TimeoutError) as exc:
        logger.warning(
            "Não foi possível gravar %d registros em %s: %s",
            len(itens),
            modelo.__tablename__,
            exc,
        )
