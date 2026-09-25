import datetime as dt
from decimal import Decimal

from sqlalchemy import BigInteger, Date, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.comum import ComAtualizacao, Moeda


class Licitacao(ComAtualizacao, Base):
    __tablename__ = "licitacoes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    situacao: Mapped[str | None] = mapped_column(String(100), nullable=True)
    modalidade: Mapped[str | None] = mapped_column(String(100), nullable=True)
    instrumento_legal: Mapped[str | None] = mapped_column(String(200), nullable=True)
    valor: Mapped[Decimal | None] = mapped_column(Moeda, nullable=True)
    unidade_gestora_codigo: Mapped[str] = mapped_column(String(10))
    orgao_codigo: Mapped[str] = mapped_column(String(10), index=True)
    data_abertura: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    data_publicacao: Mapped[dt.date | None] = mapped_column(Date, nullable=True)

    __table_args__ = (
        Index("ix_licitacoes_data_orgao", "data_abertura", "orgao_codigo"),
    )
