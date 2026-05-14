---
description: Explica como algo funciona no projeto sem poluir o contexto principal
---

Invoque o subagent `explorer` para responder: $ARGUMENTS

O subagent deve:

1. Identificar arquivos relevantes via Grep/Glob
2. Ler apenas as partes necessárias (não arquivos inteiros)
3. Sintetizar resposta em até 200 palavras
4. Citar arquivo:linha para todas as afirmações
5. Sugerir próximos arquivos a explorar se quiser aprofundar

## Após receber a resposta do subagent

Apresente ao usuário no formato:

```
[resposta do subagent — prosa concisa com referências]

---

Quer que eu:
- Aprofunde em algum ponto específico?
- Mostre o código fonte de algum dos arquivos referenciados?
- Faça uma mudança baseada nesse entendimento?
```

Não execute mudanças sem confirmação do usuário.