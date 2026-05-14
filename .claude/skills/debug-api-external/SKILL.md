---
name: debug-api-external
description: Diagnostica problemas de integração com a API do Portal da Transparência. Use quando endpoints retornam 502/504, dados vêm vazios ou com formato inesperado, há suspeita de rate limit, autenticação falha, ou o cliente HTTPX apresenta erro. Cobre análise sistemática de logs, requests, headers, payload e respostas. Evita "tentativa e erro" propondo um caminho de diagnóstico ordenado.
---

# Debug de integração com API externa

Você está diagnosticando um problema de comunicação com a API do Portal da Transparência. Siga o método científico: hipótese, evidência, conclusão. Não chute soluções.

## Antes de qualquer coisa: capture os sintomas

Pergunte ou colete:

1. **Mensagem de erro exata** (não parafraseada)
2. **Endpoint nosso que está falhando** e parâmetros usados
3. **Frequência**: sempre? intermitente? começou agora?
4. **Mudou algo recentemente?** (deploy, atualização de dependência, mudança de chave)
5. **Funciona via curl direto na API do Portal?**

Sem esses dados, está chutando.

## Mapa de problemas comuns

| Sintoma | Causa provável | Onde investigar |
|---|---|---|
| `401 Unauthorized` | Chave inválida ou expirada | Header `chave-api-dados` |
| `403 Forbidden` | Chave válida mas sem permissão para o endpoint | Documentação do Portal |
| `429 Too Many Requests` | Rate limit estourado | Frequência de chamadas, cache |
| `404 Not Found` | Path errado ou recurso inexistente | URL construída no client |
| `500/502/503 do upstream` | Problema no Portal | https://portaldatransparencia.gov.br (status) |
| `httpx.ConnectError` | DNS, firewall, ou Portal fora | Network, `curl` direto |
| `httpx.TimeoutException` | Resposta demorou demais | Timeout do client, query pesada |
| Resposta vazia mas 200 | Filtros excluem tudo, ou dados não existem para período | Parâmetros enviados |
| Campos faltando na resposta | Portal mudou schema | Comparar com Swagger oficial |
| `json.JSONDecodeError` | Portal retornou HTML (ex: página de erro) | `response.text` antes do `.json()` |

## Processo de diagnóstico (siga em ordem)

### Etapa 1: Reproduzir isoladamente

Crie um script mínimo que reproduza o problema sem passar pela API FastAPI:

```python
# debug_repro.py
import asyncio
import httpx
import os

API_KEY = os.environ["TRANSPARENCIA_API_KEY"]

async def main():
    async with httpx.AsyncClient(
        base_url="https://api.portaldatransparencia.gov.br/api-de-dados",
        headers={"chave-api-dados": API_KEY},
        timeout=30.0,
    ) as client:
        # Substitua pelo endpoint e parâmetros suspeitos
        response = await client.get("/viagens", params={"codigoOrgao": "26000", "pagina": 1})

        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body (primeiros 500 chars): {response.text[:500]}")

asyncio.run(main())
```

Rode:

```bash
python debug_repro.py
```

Se o script reproduz, o problema está no lado deles ou na request. Se não reproduz, o problema está no nosso código.

### Etapa 2: Comparar com curl direto

```bash
curl -v \
  -H "chave-api-dados: $TRANSPARENCIA_API_KEY" \
  -H "Accept: application/json" \
  "https://api.portaldatransparencia.gov.br/api-de-dados/viagens?codigoOrgao=26000&pagina=1"
```

Notas:

- `-v` mostra request e response completos
- Se curl funciona e nosso código não, há diferença no que enviamos
- Compare headers, params, ordem

### Etapa 3: Inspecionar request real do HTTPX

Adicione logging temporário ou use `event_hooks`:

```python
async def log_request(request: httpx.Request):
    print(f">>> {request.method} {request.url}")
    print(f">>> Headers: {dict(request.headers)}")

async def log_response(response: httpx.Response):
    await response.aread()
    print(f"<<< {response.status_code}")
    print(f"<<< Body: {response.text[:300]}")

client = httpx.AsyncClient(
    event_hooks={"request": [log_request], "response": [log_response]},
    # ...
)
```

Ou aumente o nível de log do httpx:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("httpx").setLevel(logging.DEBUG)
```

### Etapa 4: Verificar autenticação

```bash
# Sua chave está correta na .env?
grep TRANSPARENCIA_API_KEY .env

# A app está lendo a chave esperada?
python -c "from app.core.config import settings; print(repr(settings.transparencia_api_key))"
```

⚠️ Sinais de problema:
- Chave vazia
- Chave com aspas extras: `"abc123"` (literal incluindo aspas)
- Chave com espaços antes/depois
- `.env` não está sendo lido (verificar `model_config`)

### Etapa 5: Verificar parâmetros enviados

A API do Portal é **bem chata** com formato. Erros comuns:

| Campo | Formato esperado | Erro comum |
|---|---|---|
| Datas | `AAAAMMDD` ou `DD/MM/AAAA` (depende do endpoint!) | Mandar ISO `2024-01-15` |
| Mês/ano | `AAAAMM` | Mandar separado |
| Códigos de órgão | string de 5 dígitos | Mandar inteiro |
| Página | começa em 1 | Mandar 0 |

Consulte sempre o Swagger oficial: https://api.portaldatransparencia.gov.br/swagger-ui/index.html

### Etapa 6: Rate limit

Limites do Portal:

- **Horário comercial (06h–00h)**: 30 requisições/minuto
- **Madrugada (00h–06h)**: 90 requisições/minuto

Se está estourando, opções:

1. **Cache** mais agressivo — primeira coisa a fazer
2. **Backoff exponencial** ao receber 429:

```python
import asyncio
import httpx


async def get_com_retry(client: httpx.AsyncClient, path: str, max_retries: int = 3):
    delay = 1.0
    for tentativa in range(max_retries):
        response = await client.get(path)
        if response.status_code != 429:
            return response

        retry_after = float(response.headers.get("Retry-After", delay))
        await asyncio.sleep(retry_after)
        delay *= 2

    raise TransparenciaAPIError("Rate limit excedido após retries")
```

3. **Semáforo** para limitar concorrência:

```python
import asyncio

_semaforo = asyncio.Semaphore(5)  # max 5 requests simultâneas

async def get_limitado(client, path):
    async with _semaforo:
        return await client.get(path)
```

### Etapa 7: Resposta com formato inesperado

Sintoma: `KeyError` ou `pydantic.ValidationError` ao parsear.

Diagnóstico:

```python
# Em vez de assumir o schema, imprima o que vem
raw = await client.get("/viagens", params={...})
print(json.dumps(raw.json(), indent=2, ensure_ascii=False)[:2000])
```

Possibilidades:

- **Portal mudou schema** — compare com Swagger atual; ajuste normalização no service
- **Lista vazia retornada como `[]`** (ok) ou `null`/`{}` (não-ok) — trate ambos
- **Resposta paginada com metadata diferente** — alguns endpoints usam `pagina/totalRegistros`, outros não
- **Encoding** — caracteres acentuados quebrados → cliente HTTPX já lida, mas confirme `response.encoding`

### Etapa 8: Erros de conexão / timeout

```python
try:
    response = await client.get(path)
except httpx.ConnectTimeout:
    # Não conseguiu nem conectar — Portal fora ou DNS
except httpx.ReadTimeout:
    # Conectou mas Portal demorou demais — query pesada
except httpx.HTTPError as e:
    # Genérico
```

Para Portal:

- ConnectTimeout: verifique status em https://portaldatransparencia.gov.br
- ReadTimeout: estamos pedindo dado pesado? reduza período, paginação menor
- Timeout repetido: aumente timeout do client, mas com prudência (não bloqueie sua API)

### Etapa 9: Dados duplicados ou faltando

Sintoma: paginação parece pular ou repetir.

Causa comum: **Portal usa paginação client-side em alguns endpoints**, então paginar muito rápido sem cache pode pegar dados em estados diferentes (raríssimo) ou simplesmente passar do total disponível.

Diagnóstico:

```python
# Conte total esperado vs total recebido
total_recebido = 0
for pagina in range(1, 100):
    items = await client.get_endpoint(pagina=pagina)
    if not items:
        break
    total_recebido += len(items)
print(f"Total: {total_recebido}")
```

## Ferramentas úteis

### Logging estruturado

Configure logs JSON para facilitar análise:

```python
import logging
import json
import sys

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "level": record.levelname,
            "msg": record.getMessage(),
            "logger": record.name,
            "time": self.formatTime(record),
        }
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log, ensure_ascii=False)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
```

### Mock para reproduzir em teste

Quando achar o problema, **escreva um teste que falharia antes**:

```python
@pytest.mark.asyncio
async def test_resposta_com_campo_faltando_nao_quebra():
    """Regressão: Portal removeu campo 'dataIda' e quebrou o parser."""
    def handler(request):
        return httpx.Response(200, json=[{"id": 1}])  # sem dataIda

    transport = httpx.MockTransport(handler)
    client = TransparenciaClient(api_key="x")
    client._client = httpx.AsyncClient(transport=transport, base_url=client.BASE_URL)

    # Esperamos exceção tipada, não KeyError genérico
    with pytest.raises(TransparenciaAPIError):
        await client.viagens_por_orgao("26000", "20240101", "20241231")
```

## Quando o problema é deles

Sinais de que o Portal está com problema (não você):

- curl direto também falha
- Status 5xx persistente
- Resposta com HTML em vez de JSON (página de manutenção)
- Vários endpoints diferentes falham simultaneamente

O que fazer:

1. Verifique https://portaldatransparencia.gov.br (página inicial responde?)
2. Confira no Twitter `@cgupr` se há aviso
3. Implemente **graceful degradation** na nossa API: cache stale serve, ou mensagem clara ao usuário ("Dados do Portal indisponíveis no momento, tente novamente em alguns minutos")
4. Retorne 503 com `Retry-After` em vez de propagar 502 cru

```python
@router.get("/viagens")
async def listar():
    try:
        return await service.listar(...)
    except TransparenciaAPIError as e:
        # Se temos cache antigo, sirva avisando
        if cache_data := cache.get(...):
            return JSONResponse(
                content={"data": cache_data, "stale": True},
                headers={"X-Cache": "STALE"},
            )
        raise HTTPException(
            status_code=503,
            detail="Portal da Transparência indisponível. Tente em alguns minutos.",
            headers={"Retry-After": "60"},
        )
```

## Checklist de diagnóstico

Antes de pedir ajuda ou desistir:

- [ ] Reproduzi com script mínimo (sem passar pela FastAPI)?
- [ ] Comparei com `curl` direto?
- [ ] Inspecionei request real (headers, params, URL)?
- [ ] Conferi a chave de API?
- [ ] Confirmei formato de datas/parâmetros vs Swagger oficial?
- [ ] Verifiquei se é rate limit (status 429)?
- [ ] Vi o body completo da resposta (não só `.json()`)?
- [ ] Checkei status do Portal?
- [ ] Escrevi teste de regressão para o bug encontrado?

## Anti-padrões

❌ Apertar refresh esperando funcionar
❌ Aumentar timeout sem entender o porquê
❌ `except Exception: pass` para "calar" o erro
❌ Hardcode da chave para "testar rapidinho" (nunca rapidinho)
❌ Ignorar 429 e seguir batendo
❌ Trocar a lib HTTP esperando que resolva
❌ Confiar que o Portal não vai mudar schema (sempre mudam)
❌ Diagnosticar em produção sem reproduzir local