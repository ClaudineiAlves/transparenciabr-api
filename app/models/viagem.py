import datetime as dt
from decimal import Decimal

from sqlalchemy import BigInteger, Date, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.comum import ComAtualizacao, Moeda


class Viagem(ComAtualizacao, Base):
    __tablename__ = "viagens"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    pcdp: Mapped[str] = mapped_column(String(30))
    situacao: Mapped[str] = mapped_column(String(50))
    tipo_viagem: Mapped[str] = mapped_column(String(20))
    beneficiario_nome: Mapped[str] = mapped_column(String(200))
    orgao_codigo: Mapped[str] = mapped_column(String(10), index=True)
    data_inicio_afastamento: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    data_fim_afastamento: Mapped[dt.date | None] = mapped_column(Date, nullable=True)
    valor_total_diarias: Mapped[Decimal] = mapped_column(Moeda)
    valor_total_passagem: Mapped[Decimal] = mapped_column(Moeda)
    valor_total_viagem: Mapped[Decimal] = mapped_column(Moeda)

    __table_args__ = (
        Index("ix_viagens_data_orgao", "data_inicio_afastamento", "orgao_codigo"),
    )
