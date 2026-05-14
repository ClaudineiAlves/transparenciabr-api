---
description: Roda a suite de testes com cobertura e analisa resultados
---

Execute a suite de testes do projeto e analise os resultados:

```bash
pytest --cov=app --cov-report=term-missing -v
```

Após executar, me apresente:

1. **Status geral**: N testes, N passed, N failed, N skipped
2. **Tempo total** da execução
3. **Cobertura total** (% atual)
4. **Módulos abaixo de 70% de cobertura** (listados com sua %)
5. **Testes que falharam** (se houver) — nome do teste + linha do assert que falhou
6. **Testes lentos** (se algum levar > 1s) — investigar se podem ser otimizados

Se houver falhas:
- Para cada falha, sugira hipótese da causa (sem corrigir)
- Pergunte se quero que você invoque a skill `debug-api-external` ou investigue

Se a cobertura total estiver abaixo de 70%:
- Sugira qual módulo priorizar para aumentar cobertura
- Não comece a escrever testes sem confirmação

Se tudo estiver OK (todos passam, cobertura > 70%):
- Confirme com ✅ e mostre o resumo
- Sugira próximos passos (ex: rodar `ruff check` se ainda não, fazer commit, etc.)