---
description: Roda auditoria completa de segurança no código
---

Invoque o subagent `code-reviewer` com foco específico em segurança. Escopo: $ARGUMENTS (se vazio, todo o projeto; se especificado, apenas arquivos/diretório indicados).

Instrua o subagent a aplicar especificamente a skill `review-security` e produzir relatório com:

1. 🔴 **Vulnerabilidades críticas** (exploitable agora)
2. 🟡 **Riscos importantes** (problemas reais mas mitigados)
3. 🟢 **Defesa em profundidade** (sugestões opcionais)

Complementar com verificações automatizadas:

```bash
# Lint de segurança via Ruff (regras S* = Bandit)
ruff check --select S .

# Auditoria de dependências (CVEs conhecidos)
pip-audit 2>&1 | head -40

# Busca por segredos no histórico
gitleaks detect --source . --no-banner 2>&1 || echo "gitleaks não instalado"

# Padrões problemáticos
grep -rn "shell=True" app/ 2>/dev/null
grep -rn "eval\(\|exec\(" app/ 2>/dev/null
grep -rn -iE "(api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]+['\"]" app/ 2>/dev/null
```

## Formato final

Apresente o relatório consolidado com:

- Resumo executivo (1 parágrafo)
- Achados por severidade (do subagent)
- Resultados das ferramentas automatizadas
- Plano de ação priorizado (top 3 a fazer primeiro)
- Estimativa de esforço (em horas) para resolver cada bloqueador

**Não corrija automaticamente.** Liste o que precisa ser feito e aguarde aprovação para iniciar correções.

Ao final, pergunte: "Quer que eu comece a corrigir os achados críticos um por um?"