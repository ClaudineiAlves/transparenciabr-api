import datetime as dt

from sqlalchemy import DateTime, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

# Dinheiro em NUMERIC, não em float: soma e comparação de valores têm de ser exatas.
Moeda = Numeric(16, 2)


class ComAtualizacao:
    """Momento em que o registro foi gravado ou atualizado a partir do Portal."""

    atualizado_em: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
