---
name: update-docs
description: Atualiza README.md, CLAUDE.md e documentação inline (docstrings, OpenAPI) após mudanças no código. Use após adicionar features, mudar setup, alterar API pública, modificar variáveis de ambiente, ou quando o usuário pedir para sincronizar docs. Garante que pessoas (recrutadores, contribuidores) e ferramentas (Claude, IDEs) tenham informação coerente.
---

# Atualizar documentação

Você está sincronizando documentação com mudanças recentes no código. Documentação desatualizada é pior que ausente — confunde quem confia nela.

## Princípios

1. **Verdade única** — uma informação vive em UM lugar canônico, outras só fazem link.
2. **Quem lê?** README é para humanos visitantes (recrutadores, devs). CLAUDE.md é para Claude e contribuidores. Docstrings são para quem está dentro do código.
3. **Mostre, não conte** — exemplos executáveis valem mais que descrição. "Como rodar" deve ter comandos copiáveis.
4. **Datado é frágil** — evite "atualizado em janeiro" em texto corrido. Datas só em changelog/release notes.
5. **Teste suas instruções** — siga seu próprio README em pasta limpa antes de declarar pronto.

## Mapa de responsabilidade

| Documento | Audiência | Conteúdo | Atualizar quando |
|---|---|---|---|
| `README.md` | Recrutador, dev externo | Visão geral, setup, demo, decisões | Feature pública nova, mudança de setup |
| `CLAUDE.md` | Claude, contribuidor | Arquitetura, convenções, padrões | Padrão novo, mudança de arquitetura |
| Docstrings | Quem lê o código | O que função/classe faz, args, retornos, raises | Mudança de assinatura ou comportamento |
| OpenAPI (FastAPI) | Consumidor da API | Endpoints, schemas, exemplos | Endpoint novo ou alterado |
| `.env.example` | Quem configura | Todas as variáveis necessárias | Variável de ambiente nova |
| `CHANGELOG.md` | Todos | Histórico versionado de mudanças | A cada release |
| Issues/Roadmap | Stakeholder | Próximos passos, débito técnico | Continuamente |

## Processo

### 1. Diagnóstico — o que mudou?

```bash
git diff main --stat                    # arquivos alterados
git log main..HEAD --oneline            # commits desde a branch base
```

Classifique cada mudança:

- **Pública** (afeta usuário/consumidor da API) → README + OpenAPI
- **Arquitetural** (afeta como o código é organizado) → CLAUDE.md
- **Operacional** (afeta como rodar/deployar) → README + `.env.example`
- **Interna** (refatoração que não muda comportamento) → docstrings apenas

### 2. README.md — atualizações por tipo de mudança

#### Adicionou endpoint(s)

Atualize a seção **"Endpoints principais"** ou **"O que faz"**:

```markdown
## 🎯 O que faz

A API expõe:

- `GET /orgaos` — lista órgãos do SIAFI com paginação
- `GET /orgaos/{codigo}` — detalhes de um órgão
- `GET /viagens?orgao=X` — viagens oficiais por órgão e período
- `GET /despesas/comparar?orgaos=X,Y` — comparação de despesas (NOVO)
```

#### Mudou setup

Atualize **"Como rodar"** garantindo que comandos sejam copiáveis:

```markdown
## 🚀 Como rodar

​```bash
# 1. Clone e entre
git clone https://github.com/SEU-USUARIO/transparencia-br-api.git
cd transparencia-br-api

# 2. Ambiente virtual
python -m venv .venv && source .venv/bin/activate

# 3. Dependências
pip install -e ".[dev]"

# 4. Configuração
cp .env.example .env
# Obtenha sua chave em https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email
# Cole em TRANSPARENCIA_API_KEY no .env

# 5. Banco (NOVO - se aplicável)
alembic upgrade head

# 6. Rode
uvicorn app.main:app --reload
​```

Acesse http://localhost:8000/docs.
```

#### Adicionou variável de ambiente

1. Atualize `.env.example` com o nome novo e comentário explicativo
2. Mencione no README na seção de setup se for obrigatória
3. Atualize `app/core/config.py` (se ainda não estava lá)

```env
# Cache TTL em segundos (default: 3600 = 1h)
CACHE_TTL_SECONDS=3600
```

#### Adicionou dependência

Já vai no `pyproject.toml`. Se for relevante para o usuário (não dev-only), mencione na seção **"Stack"** do README.

#### Adicionou screenshot/demo

Capture um gif curto (10-15s) com `peek` (Linux), `licecap` (Mac) ou `ScreenToGif` (Windows). Coloque em `docs/img/demo.gif` e referencie:

```markdown
## 🎬 Demo

![Demo da TransparênciaBR API](docs/img/demo.gif)
```

### 3. CLAUDE.md — atualizações por tipo de mudança

#### Padrão arquitetural novo

Exemplo: "agora usamos repositórios para acesso a dados". Adicione/atualize seção de arquitetura:

```markdown
### Camada de Repositório (NOVO)

Entre `services/` e `models/` temos `repositories/` para encapsular acesso a dados.

​```
service → repository → model (SQLAlchemy)
​```

Por quê? Permite trocar implementação (SQL → cache → fake) sem alterar service.
```

#### Convenção nova

Atualize seção "Convenções de código". Inclua exemplo do certo e do errado.

#### Anti-padrão descoberto

Adicione à seção "Anti-padrões a evitar" da skill relevante.

### 4. Docstrings — padrão do projeto

Use **estilo Google**, em português:

```python
async def listar_viagens_por_orgao(
    codigo_orgao: str,
    data_inicio: date,
    data_fim: date,
) -> list[ViagemResponse]:
    """Lista viagens oficiais de um órgão num período.

    Consulta a API do Portal da Transparência e normaliza a resposta
    para o schema interno. Aplica cache de 1h por combinação de parâmetros.

    Args:
        codigo_orgao: Código SIAFI do órgão (5 dígitos).
        data_inicio: Data inicial do período (inclusiva).
        data_fim: Data final do período (inclusiva).

    Returns:
        Lista de viagens normalizadas, ordenadas por data decrescente.
        Lista vazia se nenhuma viagem encontrada.

    Raises:
        TransparenciaAPIError: Se a API externa retornar erro ou timeout.
        ValueError: Se codigo_orgao não tiver formato esperado.
    """
```

**Quando docstring é obrigatória:**

- Funções públicas (sem `_` no início)
- Classes
- Módulos (no topo do arquivo)
- Funções com mais de 10 linhas
- Qualquer função em `services/` ou `api/`

**Quando é dispensável:**

- Funções privadas triviais (`_format_date`)
- Getters/setters de uma linha
- Funções com nome auto-explicativo e até 5 linhas

### 5. OpenAPI (FastAPI) — descrições nos endpoints

FastAPI gera docs automaticamente de:

- `summary` do decorator: linha curta que aparece na lista
- `description`: explicação longa (markdown OK)
- `response_model`: schema de saída
- `responses`: status codes não-default e seus schemas
- `tags`: agrupamento

```python
@router.get(
    "/viagens",
    response_model=ViagemListResponse,
    summary="Lista viagens oficiais",
    description="""
Retorna viagens oficiais pagas pelo governo federal num período.

**Filtros:**
- `orgao`: código SIAFI (5 dígitos)
- `data_inicio` / `data_fim`: período em AAAA-MM-DD

**Cache:** respostas são cacheadas por 1 hora.

**Rate limit do upstream:** 30 req/min em horário comercial.
    """,
    responses={
        400: {"description": "Parâmetros inválidos"},
        502: {"description": "Erro na API do Portal da Transparência"},
    },
)
```

Use `example` ou `examples` nos schemas Pydantic para Swagger mostrar input de teste:

```python
class ViagemFilter(BaseModel):
    orgao: str = Field(min_length=5, max_length=5, examples=["26000"])
    data_inicio: date = Field(examples=["2024-01-01"])
```

### 6. CHANGELOG.md (quando o projeto crescer)

Adote [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/):

```markdown
# Changelog

Todas as mudanças notáveis neste projeto são documentadas aqui.

## [Não lançado]

### Adicionado
- Endpoint `/despesas/comparar` para comparação entre órgãos
- Cache em memória com TTL de 1h

### Alterado
- `/viagens` agora aceita filtro de data obrigatório

### Corrigido
- Erro 500 quando API externa retornava 204

## [0.1.0] - 2026-05-13

### Adicionado
- Versão inicial: endpoints de saúde, órgãos e viagens
- Autenticação JWT
- Frontend HTMX
```

### 7. Roadmap (issues/README)

Se o README tem seção de Roadmap, marque itens concluídos com `[x]` e adicione próximos passos:

```markdown
## 📋 Roadmap

- [x] Estrutura inicial + health check
- [x] Cliente assíncrono da API do Portal
- [x] Autenticação JWT (NOVO ✨)
- [x] Endpoints de servidores e viagens
- [ ] Cache distribuído com Redis
- [ ] Rate limiting por usuário
- [ ] Deploy em produção
```

## Checklist final

Antes de fechar a tarefa, valide:

- [ ] Clone o projeto em pasta limpa OU `cd /tmp && cp -r projeto-copy . && cd projeto-copy`
- [ ] Siga literalmente as instruções do README — funciona até abrir `/docs`?
- [ ] Toda variável de ambiente nova está em `.env.example` com comentário
- [ ] Todo endpoint novo aparece em `/docs` com summary e description úteis
- [ ] CLAUDE.md menciona qualquer padrão arquitetural novo
- [ ] Docstrings em funções públicas de `services/` e `api/`
- [ ] Sem TODOs órfãos em docs ("FIXME: explicar isso")
- [ ] Links no README funcionam (curl -I ou abrir manualmente)
- [ ] Roadmap marca o que foi feito

## Anti-padrões

❌ "Veja o código" — se precisa ler código pra entender, falta documentação
❌ Copiar descrição do código pra docstring sem agregar valor
❌ Datas no texto que vão envelhecer ("Em janeiro de 2026 adicionamos...")
❌ Capturas de tela desatualizadas
❌ Comandos de setup que não foram testados
❌ Manter seções que descrevem comportamento que mudou
❌ Documentação extensa onde algo simples bastaria
❌ Promessa de feature ("em breve adicionaremos...") sem rastreamento em issue

## Para o portfólio especificamente

Documentação é **a primeira impressão**. Um recrutador olha em 60 segundos:

1. Título e descrição de 1 linha — clara?
2. Stack — moderna?
3. Demo (gif/screenshot) — visual em 5s?
4. Como rodar — copiável e curto?
5. Decisões técnicas — você pensou ou só seguiu tutorial?

Capriche **especialmente** nessas 5 partes.