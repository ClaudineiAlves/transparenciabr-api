# Transparência BR API

[![CI](https://github.com/ClaudineiAlves/transparenciabr-api/actions/workflows/ci.yml/badge.svg)](https://github.com/ClaudineiAlves/transparenciabr-api/actions/workflows/ci.yml)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)
![PostgreSQL 16](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)

API REST assíncrona que expõe quatro datasets do [Portal da Transparência da CGU](https://portaldatransparencia.gov.br/) — cartões corporativos, viagens a serviço, contratos e licitações — em endpoints versionados `/v1/`, com documentação Swagger/ReDoc gerada do próprio código. Cada página consultada é validada, normalizada e gravada em PostgreSQL, e o que já foi gravado pode ser filtrado por órgão, período e faixa de valor sem chamar o Portal de novo.

**Demo:** [página de busca](https://transparenciabr-api.onrender.com/) para consultar os dados sem escrever código, ou [Swagger](https://transparenciabr-api.onrender.com/docs) para testar os endpoints. Hospedado no plano gratuito do Render; a primeira requisição após um período ocioso pode levar até um minuto.

## Decisões de engenharia

- **Camadas explícitas.** `api/v1` (rotas), `services` (regra de negócio), `clients` (integração com o Portal), `repositories` (acesso ao banco), `schemas` (contratos Pydantic), `models` (ORM) e `core` (configuração, banco e exceções). A regra de negócio não conhece o FastAPI nem o formato da API externa.
- **Integração resiliente.** O cliente `httpx` tem timeout explícito e faz retry automático quando o Portal responde `429`, respeitando o header `Retry-After`. Exceções próprias (`PortalIndisponivel`, `ParametrosInvalidos`) são tratadas em handlers centralizados: erro ou indisponibilidade do Portal vira resposta previsível da API, não stack trace.
- **Testes que não dependem da fonte.** pytest + pytest-asyncio cobrindo os quatro recursos, com o Portal mockado via `pytest-httpx`: a suíte roda mesmo quando a API do governo está fora.
- **Ingestão com consulta local.** Cada página vinda do Portal passa pelos schemas Pydantic, é normalizada — datas em `DATE`, valores em `NUMERIC(16, 2)`, inclusive o texto `"1.234,56"` dos cartões — e gravada em background com upsert por `id`. Repetir uma consulta atualiza o registro em vez de duplicar, e a resposta não espera o banco. As rotas `/v1/{recurso}/armazenados` filtram o que já foi gravado por órgão, período e faixa de valor.
- **Falha isolada.** Se o PostgreSQL cair, ou se `DATABASE_URL` não existir, as rotas do Portal continuam respondendo e só a consulta local devolve `503`. O `/health` não toca no banco, para um Postgres serverless poder dormir quando não há uso.
- **Migrations versionadas.** SQLAlchemy 2 assíncrono (`asyncpg`) e Alembic: o ambiente sobe do zero com `alembic upgrade head`. A segunda migration converte as colunas de texto da primeira em `DATE` e `NUMERIC` sem perder dados (aceita `DD/MM/AAAA` e `AAAA-MM-DD`) e tem downgrade.
- **Operação.** `GET /health`, CORS configurado e imagem Docker que lê a porta da variável `PORT`, com deploy no Render via blueprint (`render.yaml`) e PostgreSQL gerenciado no Neon.

## Stack

| Camada | Tecnologia |
|---|---|
| API | FastAPI, Pydantic |
| Banco | PostgreSQL, SQLAlchemy 2 (async), asyncpg, Alembic |
| Integração | httpx (async) |
| Testes e qualidade | pytest, pytest-asyncio, pytest-httpx, pytest-cov, ruff |
| Infra | Docker, Docker Compose, GitHub Actions |

## Como rodar

Você vai precisar de uma chave da API do Portal da Transparência ([solicitar aqui](https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email)).

### Com Docker

```bash
cp .env.example .env                          # preencha TRANSPARENCIA_API_KEY
docker compose up -d --build                  # sobe PostgreSQL 16 + API
docker compose exec app alembic upgrade head  # cria as tabelas
```

A API fica em `http://localhost:8000`: documentação interativa em `/docs` (Swagger) e `/redoc`, health check em `/health`. A raiz (`/`) serve uma página HTML (`static/index.html`) que consulta os quatro endpoints.

### Sem Docker

Requisitos: Python 3.11+ e, para gravar e consultar, um PostgreSQL acessível.

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

cp .env.example .env           # edite com suas credenciais
alembic upgrade head
uvicorn app.main:app --reload
```

Variáveis de ambiente:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/transparencia_br
TRANSPARENCIA_API_KEY=sua_chave_aqui
```

`DATABASE_URL` é opcional: sem ela, a API funciona só como proxy do Portal. URLs `postgres://` e `postgresql://` e as que trazem `sslmode=require` (Neon, Render, Supabase) são convertidas automaticamente para o formato do `asyncpg`.

## Endpoints

Todos os recursos são paginados pelo parâmetro `pagina` e respondem com schemas Pydantic (`Pagina[...]`).

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

### Consulta local — `GET /v1/{recurso}/armazenados`

Consulta o que já foi gravado, sem chamar o Portal. Existe para os quatro recursos: `cartoes`, `viagens`, `contratos` e `licitacoes`.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `codigo_orgao` | string | Código SIAFI do órgão |
| `data_de`, `data_ate` | data (`AAAA-MM-DD`) | Período |
| `valor_min`, `valor_max` | número | Faixa de valor, em reais |
| `pagina`, `tamanho` | int | Paginação (tamanho padrão 50, máximo 500) |

| Recurso | Data filtrada | Valor filtrado |
|---------|---------------|----------------|
| cartões | data da transação | valor da transação |
| viagens | início do afastamento | valor total da viagem |
| contratos | data de assinatura | valor final |
| licitações | data de abertura | valor |

A resposta traz `pagina`, `tamanho`, `total` e `itens`, do mais recente para o mais antigo. Sem banco, devolve `503`.

**Exemplo:**

```bash
curl "http://localhost:8000/v1/contratos/armazenados?codigo_orgao=26000&data_de=2025-01-01&data_ate=2025-01-31&valor_min=10000"
```

### `GET /health`

Health check da aplicação, para monitoramento e para a plataforma de deploy.

## Testes e qualidade

Os testes chamam a aplicação em processo (`httpx.ASGITransport`) e mockam o Portal com `pytest-httpx`. Para cada recurso, cobrem a página de resultados e o Portal indisponível; os de cartões também cobrem o parâmetro de paginação e a falta de filtros obrigatórios, e os de licitações, parâmetros inválidos.

Os de persistência e consulta local usam um PostgreSQL de verdade e cobrem a gravação normalizada, o upsert sem duplicar, o texto maior que a coluna, o banco fora do ar sem derrubar o proxy, os filtros por órgão, período e valor, a paginação e a validação. Localmente, suba o banco com `docker compose up -d db` e rode `alembic upgrade head`; sem banco, esses testes são pulados (no CI, a falta do banco é erro).

```bash
pytest --cov=app --cov-report=term-missing   # testes com cobertura
ruff check . && ruff format --check .        # lint e formatação
```

O [workflow de CI](.github/workflows/ci.yml) roda a cada push e pull request na `main`, em dois jobs:

- **lint:** `ruff check` e `ruff format --check`;
- **test:** sobe um PostgreSQL 16 como serviço, aplica as migrations e roda o pytest com `--cov-fail-under=70`, ou seja, o build quebra se a cobertura cair abaixo de 70%.

Nova migration depois de alterar os models:

```bash
alembic revision --autogenerate -m "descrição"
alembic upgrade head
```

## Estrutura

```
app/
  main.py              # app FastAPI, lifespan, CORS, handlers de exceção, /health
  core/
    config.py          # settings via pydantic-settings (DATABASE_URL opcional)
    database.py        # engine async + sessão + Base ORM
    exceptions.py      # PortalIndisponivel, ParametrosInvalidos, BancoIndisponivel
  api/v1/              # rotas versionadas (uma por recurso) + /armazenados
  clients/
    transparencia.py   # cliente httpx com timeout e retry em 429
  services/            # regra de negócio, normalização e gravação em background
  repositories/        # upsert e consultas no PostgreSQL
  schemas/             # contratos Pydantic de entrada e saída
  models/              # modelos SQLAlchemy
alembic/               # migrations: criação das tabelas; datas e valores tipados
static/index.html      # página servida na raiz
tests/                 # pytest + pytest-asyncio + pytest-httpx
Dockerfile
docker-compose.yml     # PostgreSQL 16 + API com reload
```

## Licença

[MIT](LICENSE).

## Autor

**Claudinei Alves Reis** — estudante de Ciência de Dados e IA na PUC-Campinas.
[LinkedIn](https://www.linkedin.com/in/claudinei-alves-reis/) · [Portfólio](https://claudineiportfolio.vercel.app)
