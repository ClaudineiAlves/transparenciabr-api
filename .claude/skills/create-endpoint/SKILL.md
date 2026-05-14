---
name: create-endpoint
description: Cria um endpoint FastAPI completo seguindo a arquitetura do projeto TransparenciaBR. Use sempre que o usuário pedir para adicionar um novo endpoint, rota, recurso ou funcionalidade que envolva HTTP. Cobre roteador, schemas Pydantic, service layer, registro no main.py, testes pytest e documentação OpenAPI. Garante separação correta entre camadas (router fino, service gordo, modelos burros).
---

# Criar endpoint completo

Você está adicionando um novo endpoint à API TransparenciaBR. Este projeto segue arquitetura em camadas estrita — siga-a sem exceção.

## Arquitetura obrigatória

```
HTTP request
     │
     ▼
app/api/<recurso>.py        ← Router: valida HTTP, chama service
     │
     ▼
app/schemas/<recurso>.py    ← Pydantic: contratos de entrada/saída
     │
     ▼
app/services/<recurso>_service.py   ← Lógica de negócio, regras
     │
     ▼
app/services/transparencia_client.py   ← Cliente HTTP externo
ou app/models/<recurso>.py             ← ORM (se persistir em banco)
```

**Regra de ouro:** routers NUNCA acessam banco ou API externa diretamente. Sempre via service.

## Processo passo a passo

Execute na ordem. Não pule passos.

### Passo 1: Esclarecer o requisito

Antes de codar, confirme com o usuário (se já não estiver claro):

- Qual recurso? (servidores, viagens, despesas, etc.)
- Qual operação? (listar, buscar por ID, criar, agregar, comparar)
- Precisa de autenticação? (default: sim, exceto endpoints públicos como /health)
- Vem da API externa ou do banco local?
- Tem paginação ou filtros?

Se faltar informação crítica, pergunte UMA pergunta objetiva e siga em frente.

### Passo 2: Criar/atualizar schemas Pydantic

Arquivo: `app/schemas/<recurso>.py`

Crie três classes (ou mais se necessário), separando claramente entrada de saída:

```python
"""Schemas Pydantic para o recurso <recurso>."""
from datetime import date
from pydantic import BaseModel, Field


class <Recurso>Filter(BaseModel):
    """Filtros de query string para listagem."""
    pagina: int = Field(default=1, ge=1, le=1000)
    data_inicio: date | None = None
    data_fim: date | None = None


class <Recurso>Response(BaseModel):
    """Representação retornada ao cliente. NUNCA exponha o modelo do banco direto."""
    id: int
    nome: str
    # ... apenas campos públicos


class <Recurso>ListResponse(BaseModel):
    """Resposta paginada padrão do projeto."""
    data: list[<Recurso>Response]
    meta: dict  # {"pagina": 1, "total": 100, "por_pagina": 20}
```

**Regras de schemas:**

- Use `Field` com restrições: `min_length`, `max_length`, `ge`, `le`, `pattern`
- Datas como `date` ou `datetime`, nunca `str`
- Schemas de saída NÃO devem expor IDs internos, hashes de senha, etc.
- Sufixos padrão: `Create` (POST), `Update` (PATCH), `Response` (GET), `Filter` (query), `DB` (interno)

### Passo 3: Criar o service (regra de negócio)

Arquivo: `app/services/<recurso>_service.py`

```python
"""Lógica de negócio do recurso <recurso>."""
from __future__ import annotations

from app.schemas.<recurso> import <Recurso>Filter, <Recurso>Response
from app.services.transparencia_client import TransparenciaClient, TransparenciaAPIError


class <Recurso>Service:
    """Encapsula operações sobre <recurso>."""

    def __init__(self, client: TransparenciaClient) -> None:
        self._client = client

    async def listar(self, filtros: <Recurso>Filter) -> list[<Recurso>Response]:
        """Lista <recurso> aplicando filtros e normalização."""
        try:
            raw = await self._client.<metodo_apropriado>(
                pagina=filtros.pagina,
                # ... outros parâmetros
            )
        except TransparenciaAPIError:
            raise  # propaga para o router converter em HTTPException

        # Normalize aqui: API externa retorna campos confusos, traduza
        return [
            <Recurso>Response(
                id=item["id"],
                nome=item["nome"],
            )
            for item in raw
        ]
```

**Regras de services:**

- Async sempre
- Recebem dependências por injeção (cliente HTTP, sessão de banco)
- NÃO conhecem detalhes de HTTP (não levantam `HTTPException`)
- Levantam exceções de domínio (`TransparenciaAPIError`, `RecursoNaoEncontrado`)
- Fazem a normalização dos dados externos para o schema da nossa API

### Passo 4: Criar o router

Arquivo: `app/api/<recurso>.py`

```python
"""Endpoints HTTP do recurso <recurso>."""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.<recurso> import <Recurso>Filter, <Recurso>ListResponse
from app.services.<recurso>_service import <Recurso>Service
from app.services.transparencia_client import TransparenciaAPIError, get_client

router = APIRouter(prefix="/<recursos>", tags=["<recursos>"])


def get_service() -> <Recurso>Service:
    """Dependency injection do service."""
    return <Recurso>Service(client=get_client())


@router.get(
    "",
    response_model=<Recurso>ListResponse,
    summary="Lista <recursos>",
    description="Retorna lista paginada de <recursos> com filtros opcionais.",
    responses={
        502: {"description": "Erro ao consultar API do Portal da Transparência"},
    },
)
async def listar_<recursos>(
    filtros: <Recurso>Filter = Depends(),
    service: <Recurso>Service = Depends(get_service),
) -> <Recurso>ListResponse:
    try:
        items = await service.listar(filtros)
    except TransparenciaAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro na API externa: {e}",
        )

    return <Recurso>ListResponse(
        data=items,
        meta={"pagina": filtros.pagina, "total": len(items)},
    )
```

**Regras de routers:**

- Async sempre
- Use `Depends()` para schemas de query string e injeção de service
- Capture exceções de domínio e converta em `HTTPException` com status code correto
- Status codes corretos: 200 (GET ok), 201 (POST criado), 204 (DELETE), 400 (validação), 401 (não autenticado), 403 (sem permissão), 404 (não achado), 502 (erro upstream)
- Documente com `summary`, `description`, e `responses` para códigos não-default
- Use `prefix` no router para evitar repetir o path em cada rota
- `tags` agrupa endpoints no Swagger UI

### Passo 5: Registrar no main.py

Edite `app/main.py`:

```python
from app.api import <recurso>  # adicione o import

# ... mais abaixo, junto com outros routers:
app.include_router(<recurso>.router)
```

### Passo 6: Criar testes

Arquivo: `tests/test_<recurso>.py`

Cubra **pelo menos** estes 4 cenários:

```python
"""Testes do endpoint /<recursos>."""
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.services.transparencia_client import TransparenciaAPIError


def test_listar_<recursos>_caminho_feliz(client: TestClient, monkeypatch) -> None:
    """Cenário normal: API externa responde, retornamos lista normalizada."""
    mock_data = [{"id": 1, "nome": "Item Teste"}]
    mock_get = AsyncMock(return_value=mock_data)
    monkeypatch.setattr(
        "app.services.transparencia_client.TransparenciaClient.<metodo>",
        mock_get,
    )

    response = client.get("/<recursos>?pagina=1")

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 1
    assert body["data"][0]["nome"] == "Item Teste"
    assert body["meta"]["pagina"] == 1


def test_listar_<recursos>_pagina_invalida(client: TestClient) -> None:
    """Pydantic rejeita página < 1."""
    response = client.get("/<recursos>?pagina=0")
    assert response.status_code == 422


def test_listar_<recursos>_api_externa_falha(client: TestClient, monkeypatch) -> None:
    """Quando a API externa quebra, retornamos 502 com mensagem clara."""
    mock_get = AsyncMock(side_effect=TransparenciaAPIError("Timeout"))
    monkeypatch.setattr(
        "app.services.transparencia_client.TransparenciaClient.<metodo>",
        mock_get,
    )

    response = client.get("/<recursos>")

    assert response.status_code == 502
    assert "Timeout" in response.json()["detail"]


def test_listar_<recursos>_lista_vazia(client: TestClient, monkeypatch) -> None:
    """Sem dados, retornamos lista vazia (200, não 404)."""
    mock_get = AsyncMock(return_value=[])
    monkeypatch.setattr(
        "app.services.transparencia_client.TransparenciaClient.<metodo>",
        mock_get,
    )

    response = client.get("/<recursos>")

    assert response.status_code == 200
    assert response.json()["data"] == []
```

**Regras de testes:**

- Mock SEMPRE da API externa — nunca bata na real durante CI
- Use `AsyncMock` (não `MagicMock`) para funções async
- Nomes descritivos: `test_<o_que>_<condicao>_<esperado>`
- Um cenário lógico por teste
- Use `monkeypatch` do pytest (built-in, não precisa de mock library extra)

### Passo 7: Validar

Rode na ordem e ajuste o que falhar:

```bash
pytest tests/test_<recurso>.py -v          # testes do recurso
ruff check app/api/<recurso>.py app/services/<recurso>_service.py app/schemas/<recurso>.py tests/test_<recurso>.py
ruff format app/api/<recurso>.py app/services/<recurso>_service.py app/schemas/<recurso>.py tests/test_<recurso>.py
mypy app/api/<recurso>.py app/services/<recurso>_service.py
```

E manualmente:

```bash
uvicorn app.main:app --reload
# abra http://localhost:8000/docs e veja se o endpoint aparece corretamente
# teste com curl ou Postman
```

### Passo 8: Commit

Use Conventional Commits. Um commit, focado, com corpo descrevendo o que e por quê:

```
feat(<recursos>): add listing endpoint with pagination

- Add Pydantic schemas with validation (page >= 1, optional date filters)
- Add <Recurso>Service with normalization from external API response
- Add router with dependency injection and 502 handling for upstream errors
- Add 4 test cases: happy path, invalid page, upstream failure, empty list

Refs: #<numero_da_issue_se_houver>
```

## Anti-padrões a evitar

❌ Acessar `httpx` ou banco direto no router
❌ Retornar o modelo do banco como response (vaza estrutura interna)
❌ Logar tokens, senhas, ou dados sensíveis no service
❌ Usar `print` em vez de logging
❌ Capturar `Exception` genérico — capture exceções específicas
❌ Endpoints síncronos (`def` em vez de `async def`) em rotas I/O bound
❌ Hardcode de URLs ou chaves no service
❌ Misturar lógica de negócio com formatação HTTP
❌ Testes que batem em API real (lentos, flaky, gastam quota)

## Checklist final

Antes de considerar feito:

- [ ] Schemas em `app/schemas/`, separados por intenção (Create/Response/Filter)
- [ ] Service em `app/services/` com lógica isolada
- [ ] Router em `app/api/` apenas com HTTP/validação
- [ ] Registro do router em `app/main.py`
- [ ] 4+ testes cobrindo caminho feliz, validação, erro upstream e edge case
- [ ] `pytest`, `ruff check`, `ruff format` passam
- [ ] Endpoint aparece em `/docs` com descrição e exemplos
- [ ] Commit segue Conventional Commits