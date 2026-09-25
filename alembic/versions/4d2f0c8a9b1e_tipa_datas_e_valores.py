"""tipa datas e valores e registra a última atualização

Revision ID: 4d2f0c8a9b1e
Revises: 618b67e76ea3
Create Date: 2026-09-24

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "4d2f0c8a9b1e"
down_revision: str | None = "618b67e76ea3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MOEDA = sa.Numeric(16, 2)

# Datas guardadas como texto na primeira migration. O Portal usa DD/MM/AAAA em
# cartões e AAAA-MM-DD nos demais recursos; os dois formatos são aceitos, e texto
# fora deles vira NULL em vez de abortar a conversão.
# (tabela, coluna, USING do upgrade, USING do downgrade, era NOT NULL)
DATAS = [
    (
        "cartoes",
        "data_transacao",
        "CASE WHEN data_transacao ~ '^[0-9]{2}/[0-9]{2}/[0-9]{4}$'"
        " THEN to_date(data_transacao, 'DD/MM/YYYY')"
        " WHEN data_transacao ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'"
        " THEN data_transacao::date END",
        "COALESCE(to_char(data_transacao, 'DD/MM/YYYY'), '')",
        True,
    ),
    (
        "contratos",
        "data_assinatura",
        "CASE WHEN data_assinatura ~ '^[0-9]{2}/[0-9]{2}/[0-9]{4}$'"
        " THEN to_date(data_assinatura, 'DD/MM/YYYY')"
        " WHEN data_assinatura ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'"
        " THEN data_assinatura::date END",
        "to_char(data_assinatura, 'YYYY-MM-DD')",
        False,
    ),
    (
        "contratos",
        "data_inicio_vigencia",
        "CASE WHEN data_inicio_vigencia ~ '^[0-9]{2}/[0-9]{2}/[0-9]{4}$'"
        " THEN to_date(data_inicio_vigencia, 'DD/MM/YYYY')"
        " WHEN data_inicio_vigencia ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'"
        " THEN data_inicio_vigencia::date END",
        "to_char(data_inicio_vigencia, 'YYYY-MM-DD')",
        False,
    ),
    (
        "contratos",
        "data_fim_vigencia",
        "CASE WHEN data_fim_vigencia ~ '^[0-9]{2}/[0-9]{2}/[0-9]{4}$'"
        " THEN to_date(data_fim_vigencia, 'DD/MM/YYYY')"
        " WHEN data_fim_vigencia ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'"
        " THEN data_fim_vigencia::date END",
        "to_char(data_fim_vigencia, 'YYYY-MM-DD')",
        False,
    ),
    (
        "licitacoes",
        "data_abertura",
        "CASE WHEN data_abertura ~ '^[0-9]{2}/[0-9]{2}/[0-9]{4}$'"
        " THEN to_date(data_abertura, 'DD/MM/YYYY')"
        " WHEN data_abertura ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'"
        " THEN data_abertura::date END",
        "to_char(data_abertura, 'YYYY-MM-DD')",
        False,
    ),
    (
        "licitacoes",
        "data_publicacao",
        "CASE WHEN data_publicacao ~ '^[0-9]{2}/[0-9]{2}/[0-9]{4}$'"
        " THEN to_date(data_publicacao, 'DD/MM/YYYY')"
        " WHEN data_publicacao ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'"
        " THEN data_publicacao::date END",
        "to_char(data_publicacao, 'YYYY-MM-DD')",
        False,
    ),
    (
        "viagens",
        "data_inicio_afastamento",
        "CASE WHEN data_inicio_afastamento ~ '^[0-9]{2}/[0-9]{2}/[0-9]{4}$'"
        " THEN to_date(data_inicio_afastamento, 'DD/MM/YYYY')"
        " WHEN data_inicio_afastamento ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'"
        " THEN data_inicio_afastamento::date END",
        "COALESCE(to_char(data_inicio_afastamento, 'YYYY-MM-DD'), '')",
        True,
    ),
    (
        "viagens",
        "data_fim_afastamento",
        "CASE WHEN data_fim_afastamento ~ '^[0-9]{2}/[0-9]{2}/[0-9]{4}$'"
        " THEN to_date(data_fim_afastamento, 'DD/MM/YYYY')"
        " WHEN data_fim_afastamento ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'"
        " THEN data_fim_afastamento::date END",
        "COALESCE(to_char(data_fim_afastamento, 'YYYY-MM-DD'), '')",
        True,
    ),
]

# Colunas de dinheiro que eram Float.
# (tabela, coluna, USING do upgrade, USING do downgrade, aceita NULL)
VALORES = [
    (
        "contratos",
        "valor_inicial",
        "valor_inicial::numeric(16, 2)",
        "valor_inicial::double precision",
        False,
    ),
    (
        "contratos",
        "valor_final",
        "valor_final::numeric(16, 2)",
        "valor_final::double precision",
        False,
    ),
    (
        "licitacoes",
        "valor",
        "valor::numeric(16, 2)",
        "valor::double precision",
        True,
    ),
    (
        "viagens",
        "valor_total_diarias",
        "valor_total_diarias::numeric(16, 2)",
        "valor_total_diarias::double precision",
        False,
    ),
    (
        "viagens",
        "valor_total_passagem",
        "valor_total_passagem::numeric(16, 2)",
        "valor_total_passagem::double precision",
        False,
    ),
    (
        "viagens",
        "valor_total_viagem",
        "valor_total_viagem::numeric(16, 2)",
        "valor_total_viagem::double precision",
        False,
    ),
]

TABELAS = ["cartoes", "contratos", "licitacoes", "viagens"]


def upgrade() -> None:
    # O NOT NULL cai antes da troca de tipo: o Alembic converte primeiro, e um texto
    # que vira NULL abortaria a conversão.
    for tabela, coluna, usando, _, _ in DATAS:
        op.alter_column(tabela, coluna, existing_type=sa.String(10), nullable=True)
        op.alter_column(
            tabela,
            coluna,
            type_=sa.Date(),
            existing_type=sa.String(10),
            existing_nullable=True,
            postgresql_using=usando,
        )

    # Texto no formato brasileiro ("1.234,56") para número; o que não for número
    # vira NULL.
    op.alter_column(
        "cartoes", "valor_transacao", existing_type=sa.String(20), nullable=True
    )
    op.alter_column(
        "cartoes",
        "valor_transacao",
        type_=MOEDA,
        existing_type=sa.String(20),
        existing_nullable=True,
        postgresql_using=(
            "CASE WHEN replace(replace(valor_transacao, '.', ''), ',', '.')"
            " ~ '^-?[0-9]+([.][0-9]+)?$'"
            " THEN replace(replace(valor_transacao, '.', ''), ',', '.')"
            "::numeric(16, 2) END"
        ),
    )

    for tabela, coluna, usando, _, aceita_nulo in VALORES:
        op.alter_column(
            tabela,
            coluna,
            type_=MOEDA,
            existing_type=sa.Float(),
            existing_nullable=aceita_nulo,
            postgresql_using=usando,
        )

    for tabela in TABELAS:
        op.add_column(
            tabela,
            sa.Column(
                "atualizado_em",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )


def downgrade() -> None:
    for tabela in TABELAS:
        op.drop_column(tabela, "atualizado_em")

    for tabela, coluna, _, usando, aceita_nulo in VALORES:
        op.alter_column(
            tabela,
            coluna,
            type_=sa.Float(),
            existing_type=MOEDA,
            existing_nullable=aceita_nulo,
            postgresql_using=usando,
        )

    op.alter_column(
        "cartoes",
        "valor_transacao",
        type_=sa.String(20),
        existing_type=MOEDA,
        existing_nullable=True,
        postgresql_using="COALESCE(replace(valor_transacao::text, '.', ','), '')",
    )
    op.alter_column(
        "cartoes", "valor_transacao", existing_type=sa.String(20), nullable=False
    )

    for tabela, coluna, _, usando, era_obrigatoria in DATAS:
        op.alter_column(
            tabela,
            coluna,
            type_=sa.String(10),
            existing_type=sa.Date(),
            existing_nullable=True,
            postgresql_using=usando,
        )
        if era_obrigatoria:
            op.alter_column(tabela, coluna, existing_type=sa.String(10), nullable=False)
