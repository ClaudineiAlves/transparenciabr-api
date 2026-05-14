# Configuração Claude Code — TransparênciaBR API

Esta pasta `.claude/` contém configuração específica do projeto para Claude Code (CLI da Anthropic).

## Estrutura

```
.claude/
├── skills/              # Workflows reutilizáveis carregados sob demanda
│   ├── create-endpoint/
│   ├── add-test/
│   ├── review-security/
│   ├── update-docs/
│   ├── debug-api-external/
│   └── add-migration/
├── agents/              # Subagents com janela de contexto isolada
│   ├── code-reviewer.md
│   ├── explorer.md
│   ├── deploy-checker.md
│   └── data-modeler.md
├── commands/            # Slash commands (atalhos de prompt)
│   ├── new-endpoint.md
│   ├── test.md
│   ├── pre-push.md
│   ├── security-audit.md
│   ├── explain.md
│   ├── review.md
│   └── deploy-check.md
└── README.md            # Este arquivo
```

## Conceitos

### Skills (em `.claude/skills/<nome>/SKILL.md`)

Workflows que o Claude **carrega automaticamente** quando o contexto bate com a `description` do frontmatter. Use para tarefas repetitivas com passos claros.

**Skills criadas:**

| Skill | Quando aciona | Para que serve |
|---|---|---|
| `create-endpoint` | Pedir endpoint/rota nova | Cria router + service + schema + teste seguindo arquitetura |
| `add-test` | Pedir testes ou melhorar cobertura | Adiciona testes pytest com mocks, AAA, fixtures |
| `review-security` | Auditoria, antes de deploy | Checklist de OWASP API Top 10 aplicado ao código |
| `update-docs` | Após mudanças, sincronizar docs | Atualiza README, CLAUDE.md, docstrings, OpenAPI |
| `debug-api-external` | Erros com API do Portal | Diagnóstico sistemático de problemas de integração |
| `add-migration` | Alterar schema de banco | Alembic + SQLAlchemy 2.0 com revisão e rollback |

### Subagents (em `.claude/agents/<nome>.md`)

Agentes especialistas com **contexto isolado**. Use quando a tarefa polui muito o contexto principal (revisar muitos arquivos, explorar codebase grande).

**Agents criados:**

| Agent | Para que serve |
|---|---|
| `code-reviewer` | Revisa PR completo, produz relatório por severidade |
| `explorer` | Responde "onde está X?" sem você ler 20 arquivos |
| `deploy-checker` | Valida prontidão para deploy em 5 categorias |
| `data-modeler` | Desenha modelos SQLAlchemy + Pydantic com justificativa |

### Slash Commands (em `.claude/commands/<nome>.md`)

Atalhos de prompt — você digita `/<nome>` e dispara um workflow pré-configurado.

**Comandos criados:**

| Comando | O que faz |
|---|---|
| `/new-endpoint <descrição>` | Cria endpoint completo via skill `create-endpoint` |
| `/test` | Roda pytest + cobertura e analisa |
| `/pre-push` | Valida tudo antes de `git push` |
| `/security-audit` | Auditoria de segurança completa |
| `/explain <pergunta>` | Explora codebase sem ler tudo |
| `/review` | Code review da branch atual |
| `/deploy-check` | Verifica prontidão para deploy |

## Como usar

### Pré-requisito

Instalar Claude Code (https://docs.anthropic.com/en/docs/claude-code/overview):

```bash
npm install -g @anthropic-ai/claude-code
```

### No projeto

Dentro da pasta do projeto:

```bash
cd transparencia-br-api
claude
```

O Claude Code carrega automaticamente:

- `CLAUDE.md` (contexto sempre presente)
- Descrições das skills em `.claude/skills/*/SKILL.md` (carrega o conteúdo só quando aciona)
- Subagents em `.claude/agents/` (disponíveis para invocação)
- Slash commands em `.claude/commands/` (disponíveis via `/`)

### Exemplos práticos

**Criar endpoint novo:**

```
/new-endpoint listar despesas por orgão com agregação mensal
```

**Diagnosticar bug:**

```
A API está retornando 502 quando passo data_inicio=2024-01-15. Use a skill debug-api-external para investigar.
```

**Antes de fazer push:**

```
/pre-push
```

**Antes de deploy em produção:**

```
/deploy-check
```

**Revisar trabalho da branch:**

```
/review
```

**Entender algo sem ler tudo:**

```
/explain como funciona o fluxo de autenticação JWT?
```

## Como adicionar mais

### Nova skill

```bash
mkdir .claude/skills/<nome>
cat > .claude/skills/<nome>/SKILL.md << 'EOF'
---
name: <nome>
description: [Quando essa skill deve ser acionada — seja específico]
---

# [Título]

[Instruções detalhadas para o Claude...]
EOF
```

A `description` é crítica — é o que faz o Claude saber quando carregar a skill. Inclua palavras-chave que o usuário provavelmente usaria.

### Novo subagent

```bash
cat > .claude/agents/<nome>.md << 'EOF'
---
name: <nome>
description: [Quando acionar este agent]
tools: Read, Grep, Glob, Bash    # restrinja ferramentas se possível
---

# <Nome>

[Você é um especialista em X...]
EOF
```

Subagents têm contexto **isolado** — não veem a conversa principal. Inclua todo o contexto necessário no arquivo.

### Novo slash command

```bash
cat > .claude/commands/<nome>.md << 'EOF'
---
description: [O que esse comando faz]
---

[Prompt que será executado quando o usuário digitar /<nome>]

Pode usar $ARGUMENTS para receber argumentos passados pelo usuário.
EOF
```

## Boas práticas

### Skills

- **Descrição específica** — "Use quando..." com gatilhos claros
- **Instruções acionáveis** — passos numerados, não filosofia
- **Exemplos concretos** — código real do projeto, não pseudocódigo
- **Anti-padrões explícitos** — diga o que NÃO fazer

### Subagents

- **Foco em uma tarefa** — code-review faz review, não cria endpoint
- **Tools restritas** — peça apenas o necessário (`Read, Grep` para explorer; não precisa de `Bash`)
- **Output estruturado** — defina formato de saída no SKILL/agent

### Commands

- **Verbos curtos** — `/test` não `/run-tests-and-coverage`
- **Combine skills + agents** — comando dispara workflow que pode envolver vários

## Referências

- [Docs do Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- [Best practices for subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)
- [Skills documentation](https://code.claude.com/docs/en/skills)