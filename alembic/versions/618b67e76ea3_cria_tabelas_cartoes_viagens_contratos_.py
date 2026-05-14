"""cria tabelas cartoes viagens contratos licitacoes

Revision ID: 618b67e76ea3
Revises:
Create Date: 2026-05-14

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "618b67e76ea3"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cartoes",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("mes_extrato", sa.String(7), nullable=False),
        sa.Column("data_transacao", sa.String(10), nullable=False),
        sa.Column("valor_transacao", sa.String(20), nullable=False),
        sa.Column("tipo_cartao_descricao", sa.String(200), nullable=False),
        sa.Column("estabelecimento_cnpj", sa.String(20), nullable=False),
        sa.Column("estabelecimento_nome", sa.String(300), nullable=False),
        sa.Column("unidade_gestora_codigo", sa.String(10), nullable=False),
        sa.Column("orgao_codigo", sa.String(10), nullable=False),
        sa.Column("portador_nome", sa.String(200), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cartoes_orgao_codigo", "cartoes", ["orgao_codigo"])
    op.create_index("ix_cartoes_mes_orgao", "cartoes", ["mes_extrato", "orgao_codigo"])

    op.create_table(
        "viagens",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("pcdp", sa.String(30), nullable=False),
        sa.Column("situacao", sa.String(50), nullable=False),
        sa.Column("tipo_viagem", sa.String(20), nullable=False),
        sa.Column("beneficiario_nome", sa.String(200), nullable=False),
        sa.Column("orgao_codigo", sa.String(10), nullable=False),
        sa.Column("data_inicio_afastamento", sa.String(10), nullable=False),
        sa.Column("data_fim_afastamento", sa.String(10), nullable=False),
        sa.Column("valor_total_diarias", sa.Float(), nullable=False),
        sa.Column("valor_total_passagem", sa.Float(), nullable=False),
        sa.Column("valor_total_viagem", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_viagens_orgao_codigo", "viagens", ["orgao_codigo"])
    op.create_index(
        "ix_viagens_data_orgao", "viagens", ["data_inicio_afastamento", "orgao_codigo"]
    )

    op.create_table(
        "contratos",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("numero", sa.String(50), nullable=False),
        sa.Column("objeto", sa.String(2000), nullable=False),
        sa.Column("situacao", sa.String(100), nullable=False),
        sa.Column("modalidade", sa.String(100), nullable=False),
        sa.Column("fornecedor_cnpj", sa.String(20), nullable=False),
        sa.Column("fornecedor_nome", sa.String(300), nullable=False),
        sa.Column("unidade_gestora_codigo", sa.String(10), nullable=False),
        sa.Column("orgao_codigo", sa.String(10), nullable=False),
        sa.Column("data_assinatura", sa.String(10), nullable=True),
        sa.Column("data_inicio_vigencia", sa.String(10), nullable=True),
        sa.Column("data_fim_vigencia", sa.String(10), nullable=True),
        sa.Column("valor_inicial", sa.Float(), nullable=False),
        sa.Column("valor_final", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contratos_orgao_codigo", "contratos", ["orgao_codigo"])
    op.create_index(
        "ix_contratos_data_orgao", "contratos", ["data_assinatura", "orgao_codigo"]
    )

    op.create_table(
        "licitacoes",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("situacao", sa.String(100), nullable=True),
        sa.Column("modalidade", sa.String(100), nullable=True),
        sa.Column("instrumento_legal", sa.String(200), nullable=True),
        sa.Column("valor", sa.Float(), nullable=True),
        sa.Column("unidade_gestora_codigo", sa.String(10), nullable=False),
        sa.Column("orgao_codigo", sa.String(10), nullable=False),
        sa.Column("data_abertura", sa.String(10), nullable=True),
        sa.Column("data_publicacao", sa.String(10), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_licitacoes_orgao_codigo", "licitacoes", ["orgao_codigo"])
    op.create_index(
        "ix_licitacoes_data_orgao", "licitacoes", ["data_abertura", "orgao_codigo"]
    )


def downgrade() -> None:
    op.drop_table("licitacoes")
    op.drop_table("contratos")
    op.drop_table("viagens")
    op.drop_table("cartoes")
