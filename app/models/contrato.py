from sqlalchemy import BigInteger, Float, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Contrato(Base):
    __tablename__ = "contratos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    numero: Mapped[str] = mapped_column(String(50))
    objeto: Mapped[str] = mapped_column(String(2000))
    situacao: Mapped[str] = mapped_column(String(100))
    modalidade: Mapped[str] = mapped_column(String(100))
    fornecedor_cnpj: Mapped[str] = mapped_column(String(20))
    fornecedor_nome: Mapped[str] = mapped_column(String(300))
    unidade_gestora_codigo: Mapped[str] = mapped_column(String(10))
    orgao_codigo: Mapped[str] = mapped_column(String(10), index=True)
    data_assinatura: Mapped[str | None] = mapped_column(String(10), nullable=True)
    data_inicio_vigencia: Mapped[str | None] = mapped_column(String(10), nullable=True)
    data_fim_vigencia: Mapped[str | None] = mapped_column(String(10), nullable=True)
    valor_inicial: Mapped[float] = mapped_column(Float)
    valor_final: Mapped[float] = mapped_column(Float)

    __table_args__ = (
        Index("ix_contratos_data_orgao", "data_assinatura", "orgao_codigo"),
    )
