---
name: add-test
description: Adiciona testes pytest para código Python/FastAPI existente. Use quando o usuário pedir cobertura de teste, mencionar que algo não tem teste, quiser melhorar coverage, ou após adicionar uma feature sem testes. Cobre testes unitários e de integração, mocks de dependências externas (HTTPX, banco), fixtures, e padrões assíncronos com pytest-asyncio.
---

# Adicionar testes pytest

Você está adicionando ou melhorando testes no projeto TransparenciaBR. Use esta skill para garantir testes consistentes, rápidos e que realmente protegem contra regressões.

## Princípios do projeto

1. **Testes rápidos** — toda a suite deve rodar em < 10 segundos. Sem isso, ninguém roda.
2. **Sem dependências externas reais** — mock a API do Portal da Transparência, banco em memória ou SQLite temporário.
3. **Determinismo** — testes não podem falhar aleatoriamente. Sem `time.sleep`, sem chamadas de rede reais, sem ordem dependente.
4. **Foco em comportamento, não implementação** — teste o que a função faz, não como faz. Refatorar não deve quebrar testes.
5. **Cobertura significativa** — 70%+ no `app/` total, 90%+ em `app/services/` e `app/api/`. Lint de coverage é falso conforto se os testes só exercitam felizes.

## Estrutura de testes

```
tests/
├── conftest.py                    # Fixtures compartilhadas
├── test_health.py                 # /health
├── test_transparencia_client.py   # Cliente HTTP externo
├── test_<recurso>.py              # Endpoints por recurso
├── unit/                          # (opcional) Testes unitários puros
│   └── test_normalizacao.py
└── integration/                   # (opcional) Testes que tocam DB ou rede
    └── test_e2e_<fluxo>.py
```

## Fixtures padrão do projeto

Em `tests/conftest.py`:

```python
"""Fixtures compartilhadas."""
import os

# Configuração ANTES de importar a app — evita erro de Settings sem SECRET_KEY
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("TRANSPARENCIA_API_KEY", "test-key")
os.environ.setdefault("DEBUG", "True")

from collections.abc import Generator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.transparencia_client import TransparenciaClient


@pytest.fixture
def client() -> TestClient:
    """Cliente HTTP de teste do FastAPI."""
    return TestClient(app)


@pytest.fixture
def mock_transparencia_client(monkeypatch) -> AsyncMock:
    """Mock do cliente da API externa. Configure return_value/side_effect no teste."""
    mock = AsyncMock(spec=TransparenciaClient)
    monkeypatch.setattr(
        "app.services.transparencia_client.get_client",
        lambda: mock,
    )
    return mock


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Headers de autenticação para endpoints protegidos. (Implementar quando JWT existir.)"""
    # Quando autenticação JWT estiver implementada:
    # token = gerar_token_teste()
    # return {"Authorization": f"Bearer {token}"}
    return {}


@pytest.fixture
def respostas_mock() -> dict:
    """Respostas exemplares da API do Portal da Transparência para reutilizar nos testes."""
    return {
        "orgaos_siafi": [
            {"codigo": "26000", "descricao": "Ministério da Educação"},
            {"codigo": "36000", "descricao": "Ministério da Saúde"},
        ],
        "viagens": [
            {
                "id": 1,
                "nome": "João Silva",
                "valorPassagens": 1500.00,
                "dataIda": "2024-03-15",
            },
        ],
    }
```

## Padrões por tipo de teste

### 1. Teste de endpoint (caminho feliz)

```python
def test_listar_orgaos_retorna_dados_normalizados(
    client: TestClient,
    mock_transparencia_client,
    respostas_mock,
) -> None:
    """Caminho feliz: API externa OK, retornamos lista normalizada."""
    # ARRANGE
    mock_transparencia_client.listar_orgaos_siafi.return_value = respostas_mock["orgaos_siafi"]

    # ACT
    response = client.get("/orgaos?pagina=1")

    # ASSERT
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 2
    assert body["data"][0]["codigo"] == "26000"
    assert body["meta"]["pagina"] == 1
```

**Padrão AAA (Arrange-Act-Assert):**
- **Arrange:** configura mocks e dados
- **Act:** uma única chamada que executa o que está sendo testado
- **Assert:** verifica resultado

Mantenha as três fases visualmente separadas (linhas em branco ou comentários).

### 2. Teste de validação de entrada

```python
def test_listar_orgaos_pagina_zero_retorna_422(client: TestClient) -> None:
    """Pydantic deve rejeitar página <= 0."""
    response = client.get("/orgaos?pagina=0")

    assert response.status_code == 422
    erros = response.json()["detail"]
    assert any(e["loc"] == ["query", "pagina"] for e in erros)


def test_listar_orgaos_pagina_excede_limite(client: TestClient) -> None:
    """Página acima de 1000 é rejeitada."""
    response = client.get("/orgaos?pagina=1001")
    assert response.status_code == 422


@pytest.mark.parametrize("pagina_invalida", [-1, 0, "abc", ""])
def test_listar_orgaos_paginas_invalidas(
    client: TestClient,
    pagina_invalida,
) -> None:
    """Vários valores inválidos rejeitados de uma vez."""
    response = client.get(f"/orgaos?pagina={pagina_invalida}")
    assert response.status_code == 422
```

Use `@pytest.mark.parametrize` para reduzir duplicação quando o mesmo teste roda com vários inputs.

### 3. Teste de erro upstream

```python
def test_listar_orgaos_quando_api_externa_falha_retorna_502(
    client: TestClient,
    mock_transparencia_client,
) -> None:
    """Erro do upstream vira 502 Bad Gateway, não 500."""
    from app.services.transparencia_client import TransparenciaAPIError
    mock_transparencia_client.listar_orgaos_siafi.side_effect = TransparenciaAPIError(
        "Connection timeout"
    )

    response = client.get("/orgaos")

    assert response.status_code == 502
    assert "Connection timeout" in response.json()["detail"]


def test_listar_orgaos_quando_api_externa_lenta_nao_trava(
    client: TestClient,
    mock_transparencia_client,
) -> None:
    """Timeout não deve travar a aplicação."""
    import httpx
    mock_transparencia_client.listar_orgaos_siafi.side_effect = (
        httpx.TimeoutException("timeout")
    )

    response = client.get("/orgaos")
    assert response.status_code in (502, 504)
```

### 4. Teste de service (unitário)

```python
"""Testes do service de órgãos sem passar pelo HTTP."""
import pytest
from unittest.mock import AsyncMock

from app.services.orgao_service import OrgaoService


@pytest.mark.asyncio
async def test_listar_normaliza_resposta_externa() -> None:
    """Service traduz campos da API externa para nosso schema."""
    mock_client = AsyncMock()
    mock_client.listar_orgaos_siafi.return_value = [
        {"codigo": "26000", "descricao": "MEC"},
    ]

    service = OrgaoService(client=mock_client)
    resultado = await service.listar(pagina=1)

    assert len(resultado) == 1
    assert resultado[0].codigo == "26000"
    assert resultado[0].nome == "MEC"  # nota: descricao → nome


@pytest.mark.asyncio
async def test_listar_resposta_vazia_retorna_lista_vazia() -> None:
    """Lista vazia da API externa = lista vazia (não erro)."""
    mock_client = AsyncMock()
    mock_client.listar_orgaos_siafi.return_value = []

    service = OrgaoService(client=mock_client)
    resultado = await service.listar(pagina=1)

    assert resultado == []
```

### 5. Teste de cliente externo

Mock o transporte HTTP, não a biblioteca. Use `httpx.MockTransport`:

```python
"""Testes do TransparenciaClient sem chamadas reais."""
import httpx
import pytest

from app.services.transparencia_client import (
    TransparenciaAPIError,
    TransparenciaClient,
)


@pytest.mark.asyncio
async def test_listar_orgaos_envia_header_de_autenticacao() -> None:
    """Cliente deve enviar a chave no header chave-api-dados."""
    captured_headers = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured_headers.update(request.headers)
        return httpx.Response(200, json=[])

    transport = httpx.MockTransport(handler)
    client = TransparenciaClient(api_key="minha-chave-teste")
    client._client = httpx.AsyncClient(
        base_url=TransparenciaClient.BASE_URL,
        headers={"chave-api-dados": "minha-chave-teste"},
        transport=transport,
    )

    await client.listar_orgaos_siafi(pagina=1)

    assert captured_headers["chave-api-dados"] == "minha-chave-teste"


@pytest.mark.asyncio
async def test_erro_429_vira_transparencia_api_error() -> None:
    """Rate limit do upstream propaga como exceção tipada."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": "rate limit"})

    transport = httpx.MockTransport(handler)
    client = TransparenciaClient(api_key="x")
    client._client = httpx.AsyncClient(
        base_url=TransparenciaClient.BASE_URL,
        transport=transport,
    )

    with pytest.raises(TransparenciaAPIError, match="429"):
        await client.listar_orgaos_siafi(pagina=1)
```

### 6. Teste de autenticação (quando JWT existir)

```python
def test_endpoint_protegido_sem_token_retorna_401(client: TestClient) -> None:
    """Acesso sem Authorization header é negado."""
    response = client.get("/me/historico")
    assert response.status_code == 401


def test_endpoint_protegido_com_token_invalido_retorna_401(client: TestClient) -> None:
    """Token malformado é negado."""
    response = client.get(
        "/me/historico",
        headers={"Authorization": "Bearer token-falso"},
    )
    assert response.status_code == 401


def test_endpoint_protegido_com_token_valido_retorna_200(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """Token válido permite acesso."""
    response = client.get("/me/historico", headers=auth_headers)
    assert response.status_code == 200
```

### 7. Teste parametrizado

Quando o mesmo teste roda com vários inputs, evite duplicação:

```python
@pytest.mark.parametrize(
    "codigo,esperado",
    [
        ("26000", "Ministério da Educação"),
        ("36000", "Ministério da Saúde"),
        ("99999", None),  # não existe
    ],
)
def test_busca_orgao_por_codigo(
    codigo: str,
    esperado: str | None,
    client: TestClient,
) -> None:
    response = client.get(f"/orgaos/{codigo}")
    if esperado is None:
        assert response.status_code == 404
    else:
        assert response.json()["nome"] == esperado
```

## Nomenclatura de testes

Use o padrão `test_<o_que>_<condicao>_<resultado>`:

✅ `test_listar_orgaos_pagina_invalida_retorna_422`
✅ `test_login_senha_errada_retorna_401`
✅ `test_normalizar_orgao_sem_descricao_usa_codigo`

❌ `test_orgaos` (vago)
❌ `test_funciona` (sem informação)
❌ `test1`, `test2` (numerados)

## Marcadores úteis

```python
@pytest.mark.slow              # > 1s, pode pular em dev rápido
@pytest.mark.integration       # toca DB real ou rede
@pytest.mark.skipif(...)       # condicional
@pytest.mark.asyncio           # função async
```

Configure em `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "slow: testes lentos",
    "integration: testes de integração",
]
```

Rode pulando os lentos: `pytest -m "not slow"`

## Cobertura

```bash
pytest --cov=app --cov-report=term-missing
pytest --cov=app --cov-report=html         # gera htmlcov/index.html
```

**Cobertura como diagnóstico, não como meta.** 100% de cobertura com asserts ruins é pior que 80% com testes que pegam bugs reais. Pergunte sempre: "este teste falharia se a função estivesse errada?"

## Anti-padrões a evitar

❌ `time.sleep()` em testes — substituir por mock ou freezegun
❌ Chamadas HTTP reais — sempre mock
❌ Testes que dependem de ordem de execução
❌ Asserts vagos: `assert response` (verdadeiro pra qualquer resposta)
❌ `try/except` para esconder falhas — deixe explodir
❌ Múltiplos cenários no mesmo teste — divida
❌ Setup massivo replicado entre testes — extraia para fixture
❌ Mockar o que está sendo testado (mocka dependências, não o sujeito)
❌ Testar getters/setters triviais (sem lógica)
❌ Comparar floats com `==` — use `pytest.approx`

## Checklist antes de concluir

- [ ] Nome do teste descreve cenário + resultado
- [ ] Padrão AAA visível (Arrange/Act/Assert)
- [ ] Mocks usam `AsyncMock` para funções async
- [ ] Sem chamadas de rede reais
- [ ] Sem `time.sleep` ou aleatoriedade
- [ ] Roda em < 100ms (a menos que marcado `slow`)
- [ ] Testes independentes (ordem não importa)
- [ ] Cobre caminho feliz + validação + erro upstream + edge case
- [ ] `pytest --cov` mostra aumento esperado
- [ ] Lint passa: `ruff check tests/`