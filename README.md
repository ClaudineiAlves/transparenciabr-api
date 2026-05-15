# Transparência BR API

API REST que agrega e expõe dados de transparência do governo federal brasileiro, consumindo o [Portal da Transparência (CGU)](https://portaldatransparencia.gov.br/).
Acesse aqui e teste: https://transparenciabr-api-production.up.railway.app/
## Stack

- **FastAPI** — framework web async
- **PostgreSQL + asyncpg** — banco de dados
- **SQLAlchemy 2 (async)** — ORM
- **Alembic** — migrações de banco
- **httpx** — cliente HTTP async para o Portal da Transparência

## Requisitos

- Python 3.11+
- PostgreSQL
- Chave de API do Portal da Transparência ([solicitar aqui](https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email))

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Configure as variáveis de ambiente:

```bash
cp .env.example .env
# edite .env com suas credenciais
```

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/transparencia_br
TRANSPARENCIA_API_KEY=sua_chave_aqui
```

Rode as migrações e suba o servidor:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

Acesse a documentação interativa em `http://localhost:8000/docs`.

## Endpoints

### `GET /v1/cartoes`

Lista gastos realizados com cartões corporativos do governo federal.

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `mes_ano_inicio` | string | sim | Mês/ano inicial (`MM/AAAA`) |
| `mes_ano_fim` | string | sim | Mês/ano final (`MM/AAAA`) |
| `pagina` | int | não | Página (default: 1) |
| `codigo_orgao` | string | não* | Código SIAFI do órgão |
| `cpf_portador` | string | não* | CPF do portador (sem pontuação) |
| `cnpj_estabelecimento` | string | não* | CNPJ do estabelecimento (sem pontuação) |

*Ao menos um filtro opcional ou período de até 12 meses é exigido pela API do Portal.

**Exemplo:**

```bash
curl "http://localhost:8000/v1/cartoes?mes_ano_inicio=01/2025&mes_ano_fim=01/2025&codigo_orgao=26000"
```

### `GET /v1/viagens`

Lista viagens a serviço realizadas por servidores federais.

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `codigo_orgao` | string | sim | Código SIAFI do órgão |
| `data_ida_de` | string | sim | Data de ida inicial (`DD/MM/AAAA`) |
| `data_ida_ate` | string | sim | Data de ida final (`DD/MM/AAAA`) |
| `data_retorno_de` | string | sim | Data de retorno inicial (`DD/MM/AAAA`) |
| `data_retorno_ate` | string | sim | Data de retorno final (`DD/MM/AAAA`) |
| `pagina` | int | não | Página (default: 1) |

**Exemplo:**

```bash
curl "http://localhost:8000/v1/viagens?codigo_orgao=26000&data_ida_de=01/01/2025&data_ida_ate=31/01/2025&data_retorno_de=01/01/2025&data_retorno_ate=31/01/2025"
```

### `GET /v1/contratos`

Lista contratos celebrados pelo governo federal.

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `codigo_orgao` | string | sim | Código SIAFI do órgão |
| `data_inicio_de` | string | sim | Data de início inicial (`DD/MM/AAAA`) |
| `data_inicio_ate` | string | sim | Data de início final (`DD/MM/AAAA`) |
| `pagina` | int | não | Página (default: 1) |

**Exemplo:**

```bash
curl "http://localhost:8000/v1/contratos?codigo_orgao=26000&data_inicio_de=01/01/2025&data_inicio_ate=31/01/2025"
```

### `GET /v1/licitacoes`

Lista licitações realizadas pelo governo federal (período máximo: 1 mês).

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `codigo_orgao` | string | sim | Código SIAFI do órgão |
| `data_inicial` | string | sim | Data de abertura inicial (`DD/MM/AAAA`) |
| `data_final` | string | sim | Data de abertura final (`DD/MM/AAAA`) |
| `pagina` | int | não | Página (default: 1) |

**Exemplo:**

```bash
curl "http://localhost:8000/v1/licitacoes?codigo_orgao=26000&data_inicial=01/01/2025&data_final=31/01/2025"
```

## Desenvolvimento

```bash
# Testes
pytest

# Lint
ruff check .
ruff format .

# Nova migration após alterar models
alembic revision --autogenerate -m "descrição"
alembic upgrade head
```

## Estrutura

```
app/
  main.py              # app FastAPI + lifespan
  core/
    config.py          # settings via pydantic-settings
    database.py        # engine async + sessão + Base ORM
  api/v1/              # rotas versionadas
  clients/
    transparencia.py   # client HTTP com retry em 429
  models/              # modelos SQLAlchemy
  schemas/             # schemas Pydantic
  services/            # lógica de negócio
alembic/               # migrações
tests/                 # pytest + pytest-asyncio
```
