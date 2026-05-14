# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

REST API that aggregates and exposes Brazilian government transparency data sourced from the [Portal da Transparência (CGU)](https://api.portaldatransparencia.gov.br/api-de-dados/). Built with FastAPI, PostgreSQL, and Alembic.

## Commands

```bash
# Dev server (local)
uvicorn app.main:app --reload

# Docker (recomendado — sobe PostgreSQL + app)
docker compose up
docker compose exec app alembic upgrade head

# Tests
pytest
pytest tests/test_cartoes.py                          # arquivo específico
pytest tests/test_cartoes.py::test_listar_gastos_retorna_pagina -v  # teste específico

# Migrations
alembic upgrade head
alembic revision --autogenerate -m "descrição"
alembic downgrade -1

# Lint / format
ruff check .
ruff format .
```

## Architecture

```
app/
  main.py              # App factory, routers, exception handlers registrados
  core/
    config.py          # Settings via pydantic-settings (lê .env)
    database.py        # AsyncEngine, AsyncSessionLocal, Base, get_db()
    exceptions.py      # PortalIndisponivel + handlers que retornam 502
  api/v1/
    router.py          # Agrega todos os routers de recurso
    cartoes.py         # GET /v1/cartoes
    viagens.py         # GET /v1/viagens
    contratos.py       # GET /v1/contratos
    licitacoes.py      # GET /v1/licitacoes
  clients/
    transparencia.py   # GET wrapper com retry automático em 429
  models/              # SQLAlchemy ORM — Cartao, Viagem, Contrato, Licitacao
  schemas/
    comum.py           # Pagina[T] (envelope de resposta), ErroDetalhe
    cartoes.py / viagens.py / contratos.py / licitacoes.py
  services/            # Lógica de negócio — chama client + constrói Pagina[T]
alembic/
  versions/            # 618b67e76ea3: criação das 4 tabelas
tests/
  conftest.py          # Fixture AsyncClient (ASGITransport, sem banco real)
  test_cartoes.py / test_viagens.py / test_contratos.py / test_licitacoes.py
```

## Endpoints

| Método | Rota | Parâmetros obrigatórios | Filtros opcionais |
|--------|------|------------------------|-------------------|
| GET | `/health` | — | — |
| GET | `/v1/cartoes` | `mes_ano_inicio`, `mes_ano_fim` | `codigo_orgao`, `cpf_portador`, `cnpj_estabelecimento`, `pagina` |
| GET | `/v1/viagens` | `codigo_orgao`, `data_ida_de`, `data_ida_ate`, `data_retorno_de`, `data_retorno_ate` | `pagina` |
| GET | `/v1/contratos` | `codigo_orgao`, `data_inicio_de`, `data_inicio_ate` | `pagina` |
| GET | `/v1/licitacoes` | `codigo_orgao`, `data_inicial`, `data_final` | `pagina` |

Toda resposta de listagem usa o envelope `Pagina[T]`:
```json
{ "pagina": 1, "itens": [ ... ] }
```

## Key Conventions

**Layering:** routes → services → (models | transparencia client). Routes nunca acessam DB ou API externa diretamente.

**Async:** `async def` em toda a stack. DB usa `AsyncSession`; HTTP usa `httpx.AsyncClient`.

**Settings:** toda config em `app/core/config.py` via `Settings` (pydantic-settings). Importar sempre via `from app.core.config import settings` — nunca `os.environ`.

**Respostas paginadas:** retornar sempre `Pagina[T]` de `app/schemas/comum.py`. Nunca retornar `list[T]` diretamente de um endpoint.

**Erros externos:** services levantam `PortalIndisponivel` para falhas de rede/HTTP. Os handlers em `app/core/exceptions.py` (registrados em `main.py`) convertem para `{"mensagem": "..."}` com status 502. Routes não fazem try/except.

**Portal da Transparência client:** base URL `https://api.portaldatransparencia.gov.br/api-de-dados/`, header `chave-api-dados` via `settings.transparencia_api_key`. Retry automático em 429 respeitando `Retry-After`.

**Migrations:** toda mudança de model exige `alembic revision --autogenerate`. Nunca editar schema diretamente no banco. O `alembic/env.py` importa `app.models` para detecção automática de tabelas.

**Tests:** mocks com `pytest-httpx` (`httpx_mock.add_response(url=re.compile(...))`). Nunca hit na API real. `conftest.py` usa `ASGITransport` — sem PostgreSQL necessário para rodar os testes.
