from sqlalchemy import BigInteger, Float, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Viagem(Base):
    __tablename__ = "viagens"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    pcdp: Mapped[str] = mapped_column(String(30))
    situacao: Mapped[str] = mapped_column(String(50))
    tipo_viagem: Mapped[str] = mapped_column(String(20))
    beneficiario_nome: Mapped[str] = mapped_column(String(200))
    orgao_codigo: Mapped[str] = mapped_column(String(10), index=True)
    data_inicio_afastamento: Mapped[str] = mapped_column(String(10))
    data_fim_afastamento: Mapped[str] = mapped_column(String(10))
    valor_total_diarias: Mapped[float] = mapped_column(Float)
    valor_total_passagem: Mapped[float] = mapped_column(Float)
    valor_total_viagem: Mapped[float] = mapped_column(Float)

    __table_args__ = (
        Index("ix_viagens_data_orgao", "data_inicio_afastamento", "orgao_codigo"),
    )
