from sqlalchemy import BigInteger, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Cartao(Base):
    __tablename__ = "cartoes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    mes_extrato: Mapped[str] = mapped_column(String(7))
    data_transacao: Mapped[str] = mapped_column(String(10))
    valor_transacao: Mapped[str] = mapped_column(String(20))
    tipo_cartao_descricao: Mapped[str] = mapped_column(String(200))
    estabelecimento_cnpj: Mapped[str] = mapped_column(String(20))
    estabelecimento_nome: Mapped[str] = mapped_column(String(300))
    unidade_gestora_codigo: Mapped[str] = mapped_column(String(10))
    orgao_codigo: Mapped[str] = mapped_column(String(10), index=True)
    portador_nome: Mapped[str] = mapped_column(String(200))

    __table_args__ = (Index("ix_cartoes_mes_orgao", "mes_extrato", "orgao_codigo"),)
