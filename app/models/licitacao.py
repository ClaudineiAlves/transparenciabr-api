from sqlalchemy import BigInteger, Float, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Licitacao(Base):
    __tablename__ = "licitacoes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    situacao: Mapped[str | None] = mapped_column(String(100), nullable=True)
    modalidade: Mapped[str | None] = mapped_column(String(100), nullable=True)
    instrumento_legal: Mapped[str | None] = mapped_column(String(200), nullable=True)
    valor: Mapped[float | None] = mapped_column(Float, nullable=True)
    unidade_gestora_codigo: Mapped[str] = mapped_column(String(10))
    orgao_codigo: Mapped[str] = mapped_column(String(10), index=True)
    data_abertura: Mapped[str | None] = mapped_column(String(10), nullable=True)
    data_publicacao: Mapped[str | None] = mapped_column(String(10), nullable=True)

    __table_args__ = (
        Index("ix_licitacoes_data_orgao", "data_abertura", "orgao_codigo"),
    )
