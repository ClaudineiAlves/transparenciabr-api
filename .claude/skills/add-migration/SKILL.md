---
name: add-migration
description: Cria, aplica e gerencia migrations de banco com Alembic + SQLAlchemy 2.0. Use sempre que adicionar/modificar modelo SQLAlchemy, alterar schema de banco, ou ao configurar Alembic pela primeira vez. Cobre geração automática, revisão manual, aplicação, rollback e troubleshooting de drift entre código e banco.
---

# Migrations com Alembic

Você está alterando o schema do banco. **Nunca** modifique tabelas direto no banco — toda mudança passa por uma migration versionada, testada e revertível.

## Princípios

1. **Migrations são código** — versionadas no Git, revisadas em PR, testadas no CI
2. **Migrations são imutáveis após merge** — nunca edite uma já aplicada em outro ambiente; faça uma nova
3. **Sempre revise o que o autogenerate criou** — nem sempre acerta (especialmente renomeações, mudanças de tipo)
4. **Pequenas e focadas** — uma migration = uma mudança lógica
5. **Reversíveis** — implemente `downgrade()` para rollback
6. **Compatíveis com versão anterior** durante deploy gradual

## Setup inicial (uma vez por projeto)

### 1. Instalar e inicializar

```bash
pip install alembic
alembic init alembic
```

Cria a estrutura:

```
alembic/
├── versions/          # migrations vão aqui
├── env.py             # configuração executada por toda migration
├── script.py.mako     # template das migrations
└── README
alembic.ini            # configuração principal
```

### 2. Configurar `alembic.ini`

```ini
[alembic]
script_location = alembic
sqlalchemy.url = driver://user:pass@localhost/dbname    # SOBRESCRITO por env.py

# Não use a URL hardcoded — leia do .env (próximo passo)
```

### 3. Configurar `alembic/env.py`

Substitua o conteúdo para integrar com o projeto:

```python
"""Alembic environment — integra com nossas configurações e modelos."""
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Carrega configurações do projeto
from app.core.config import settings
from app.core.database import Base

# Importar TODOS os modelos para que o autogenerate veja
from app.models import user  # noqa: F401
# from app.models import outro_modelo  # adicione aqui ao criar

config = context.config

# Sobrescreve a URL com a do .env
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Gera SQL sem conectar (útil para revisar)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,            # detecta mudança de tipo
        compare_server_default=True,  # detecta mudança de default
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica migrations no banco real."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 4. Criar `app/core/database.py`

```python
"""Configuração do banco e sessão SQLAlchemy."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Base declarativa para todos os modelos."""


engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency injection da sessão."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

E adicione em `app/core/config.py`:

```python
class Settings(BaseSettings):
    # ...
    database_url: str = "sqlite:///./dev.db"  # padrão para dev
```

## Workflow padrão de migration

### Passo 1: Alterar/criar modelo

Exemplo: criando o modelo `User` em `app/models/user.py`:

```python
"""Modelo de usuário."""
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
```

### Passo 2: Importar o modelo no `env.py`

Sem isso, o autogenerate **não vê** a tabela:

```python
# em alembic/env.py
from app.models import user  # noqa: F401
```

### Passo 3: Gerar migration automaticamente

```bash
alembic revision --autogenerate -m "create users table"
```

Cria `alembic/versions/abc123def_create_users_table.py`:

```python
"""create users table

Revision ID: abc123def456
Revises:
Create Date: 2026-05-13 14:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "abc123def456"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
```

### Passo 4: REVISAR a migration gerada ⚠️

**Não confie cegamente no autogenerate.** Erros comuns:

- **Não detecta renomeação** — vê drop + create. Edite manualmente para usar `op.alter_column` com `new_column_name`
- **Não detecta mudanças sutis de tipo** — `String(100)` → `String(200)` às vezes passa batido
- **Constraints nomeadas** podem ficar com nome diferente do esperado
- **Defaults do servidor vs Python** — diferença sutil

Compare com o que você queria. Edite se necessário.

### Passo 5: Aplicar localmente

```bash
alembic upgrade head        # aplica todas pendentes
alembic upgrade +1          # aplica só a próxima
```

Verifique:

```bash
alembic current              # versão atual
alembic history --verbose    # histórico
```

E confira o schema:

```bash
sqlite3 dev.db ".schema users"
# ou para Postgres:
psql -d transparencia -c "\d users"
```

### Passo 6: Testar rollback

```bash
alembic downgrade -1   # volta uma versão
alembic upgrade head   # reaplica
```

Se rollback quebra, sua migration **não é segura**. Conserte antes de fazer commit.

### Passo 7: Commit

```bash
git add alembic/versions/abc123_create_users_table.py app/models/user.py
git commit -m "feat(db): add users table with email and password

- Add User model with email (unique, indexed), hashed_password, is_active, created_at
- Generate Alembic migration abc123_create_users_table
- Tested upgrade and downgrade locally on SQLite"
```

## Padrões para mudanças específicas

### Adicionar coluna nullable (seguro)

```python
def upgrade():
    op.add_column("users", sa.Column("nome_completo", sa.String(200), nullable=True))

def downgrade():
    op.drop_column("users", "nome_completo")
```

Não quebra dados existentes. Pode aplicar em produção sem downtime.

### Adicionar coluna NOT NULL (cuidado)

Em duas migrations:

**Migration 1** — adiciona nullable e popula:

```python
def upgrade():
    op.add_column("users", sa.Column("nome_completo", sa.String(200), nullable=True))
    op.execute("UPDATE users SET nome_completo = email WHERE nome_completo IS NULL")
```

**Migration 2** (deploy depois que código novo já está rodando) — torna NOT NULL:

```python
def upgrade():
    op.alter_column("users", "nome_completo", nullable=False)
```

Esse padrão **expand → migrate → contract** evita downtime.

### Renomear coluna

Autogenerate vê como drop + create — você perde os dados. Edite para:

```python
def upgrade():
    op.alter_column("users", "email", new_column_name="email_address")

def downgrade():
    op.alter_column("users", "email_address", new_column_name="email")
```

### Mudar tipo de coluna

```python
def upgrade():
    op.alter_column(
        "users",
        "telefone",
        existing_type=sa.String(20),
        type_=sa.String(30),
        existing_nullable=True,
    )
```

Atenção: alguns bancos (Postgres) podem precisar `USING ...::tipo` para casts não-triviais:

```python
op.execute("ALTER TABLE users ALTER COLUMN idade TYPE INTEGER USING idade::integer")
```

### Adicionar índice

```python
def upgrade():
    op.create_index("ix_users_created_at", "users", ["created_at"])

def downgrade():
    op.drop_index("ix_users_created_at", table_name="users")
```

Em Postgres com tabela grande, use `postgresql_concurrently=True` para não bloquear writes:

```python
op.create_index("ix_users_created_at", "users", ["created_at"], postgresql_concurrently=True)
```

### Data migration (mudar dados, não estrutura)

```python
def upgrade():
    # Cria coluna
    op.add_column("users", sa.Column("role", sa.String(20), nullable=True))

    # Popula
    op.execute("UPDATE users SET role = 'admin' WHERE email LIKE '%@admin.com'")
    op.execute("UPDATE users SET role = 'user' WHERE role IS NULL")

    # Torna NOT NULL
    op.alter_column("users", "role", nullable=False)
```

## Testes envolvendo migrations

### Banco de teste limpo a cada execução

Em `tests/conftest.py`:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base


@pytest.fixture(scope="session")
def test_engine():
    """Engine SQLite em memória — rápido."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)   # cria schema direto do código
    yield engine
    engine.dispose()


@pytest.fixture
def test_db(test_engine):
    """Sessão isolada por teste com rollback automático."""
    connection = test_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    yield session
    session.close()
    transaction.rollback()
    connection.close()
```

⚠️ Para testes use `Base.metadata.create_all` (rápido), **mas tenha um teste separado** que aplica as migrations reais e compara com `Base.metadata` — pega drift entre código e migrations.

### Testar que migrations + modelos batem

```python
import subprocess
from sqlalchemy import inspect

def test_migrations_match_models(test_engine):
    """Schema gerado por migrations deve bater com Base.metadata."""
    # Aplica migrations num banco vazio
    subprocess.run(["alembic", "upgrade", "head"], check=True)

    # Compara
    inspector = inspect(test_engine)
    tabelas_no_banco = set(inspector.get_table_names())
    tabelas_em_codigo = set(Base.metadata.tables.keys())

    assert tabelas_no_banco == tabelas_em_codigo
```

## Troubleshooting

### "Target database is not up to date"

O banco está em versão anterior à `head`. Aplique:

```bash
alembic upgrade head
```

### "Can't locate revision identified by 'xyz'"

Você deletou um arquivo de migration que estava aplicado. Reverta o delete ou rode:

```bash
alembic stamp head   # marca o banco como na versão atual SEM aplicar mudança
```

⚠️ Só use `stamp` se souber exatamente o que está fazendo.

### Autogenerate não detecta mudanças

Causas comuns:

1. **Esqueceu de importar o modelo** em `env.py`
2. `target_metadata` não está apontando para o `Base` correto
3. O modelo está fora do `Base.metadata` (esqueceu de herdar de `Base`)
4. Está rodando contra um banco diferente do que pensa

### Migrations conflitantes em branches diferentes

Duas branches geraram migrations com `down_revision` igual. Faça merge:

```bash
alembic merge -m "merge migrations" rev1 rev2
```

### Banco em produção drifted (alguém alterou manual)

1. Gere uma migration "vazia": `alembic revision -m "fix prod drift"`
2. Adicione os ALTERs necessários manualmente para que produção bata com o código
3. Aplique e nunca mais altere manualmente

## Boas práticas

✅ **Uma migration = uma mudança lógica.** Não junte "add users table" com "add posts table" se foram trabalhos separados.

✅ **Nome descritivo.** `add_email_index_to_users`, não `update_table`.

✅ **Teste `downgrade` antes de fazer merge.** Se você não consegue reverter localmente, ninguém vai conseguir em produção.

✅ **Backup antes de aplicar em produção.** Sempre.

✅ **Para tabelas grandes, considere janelas de manutenção.** `ALTER TABLE` bloqueia em alguns bancos.

✅ **Use `postgresql_concurrently=True` para índices em produção Postgres.**

✅ **Documente migrações destrutivas** no commit message (drop column, drop table).

## Anti-padrões

❌ Editar migration que já foi aplicada em qualquer outro ambiente (mesmo dev de colega)
❌ Migration sem `downgrade` (deixa "pass" e ora pra nunca precisar)
❌ Misturar mudança de schema com mudança de dados sem necessidade
❌ Autogenerate "no escuro" sem revisar
❌ Aplicar `alembic stamp` aleatoriamente para "consertar"
❌ Hardcode de URL de banco em `alembic.ini` (use `env.py` + settings)
❌ Esquecer de adicionar o novo modelo em `env.py`
❌ Migrations que dependem de dados específicos do banco do dev (ex: `UPDATE WHERE id = 42`)

## Checklist final

- [ ] Modelo SQLAlchemy criado/modificado em `app/models/`
- [ ] Import do modelo adicionado em `alembic/env.py`
- [ ] Migration gerada com `alembic revision --autogenerate -m "..."`
- [ ] Migration revisada manualmente (drop+create deveria ser rename?)
- [ ] `upgrade` aplica sem erro: `alembic upgrade head`
- [ ] `downgrade` reverte sem erro: `alembic downgrade -1` e `alembic upgrade head`
- [ ] Schema do banco bate com o esperado (`\d` ou `.schema`)
- [ ] Testes passam: `pytest`
- [ ] Commit com nome descritivo e Conventional Commits
- [ ] PR menciona a mudança de schema explicitamente