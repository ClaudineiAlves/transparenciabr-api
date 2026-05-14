---
description: Revisa o código modificado na branch atual (code review completo)
---

Invoque o subagent `code-reviewer` para revisar as mudanças desta branch contra `main`.

Escopo padrão: `git diff main..HEAD`. Se o usuário passou argumentos em $ARGUMENTS (ex: nome de arquivo específico), foque nele.

O subagent deve produzir relatório estruturado com:

1. **Resumo da mudança** (o que foi feito)
2. **Verificações automáticas** (lint, format, type check, testes — com saída real)
3. **Achados por severidade:**
   - 🔴 Crítico (bloqueia merge)
   - 🟡 Importante (corrigir antes do merge)
   - 🟢 Sugestões (melhorias opcionais)
4. **Pontos positivos observados** (2-3 mínimo)
5. **Métricas** (linhas +/-, arquivos, testes adicionados, cobertura)
6. **Recomendação final** (aprovar / corrigir / refazer)

## Após receber o relatório

Apresente ao usuário e pergunte:

```
Quer que eu:
1. Corrija os achados críticos automaticamente?
2. Aborde um achado específico (qual número)?
3. Apenas faça commit das mudanças como estão?
4. Atualize algum trecho específico?
```

Não corrija nada antes de confirmação. Se o usuário pedir correção, faça uma de cada vez (mostrar diff, aplicar, mostrar próximo achado).