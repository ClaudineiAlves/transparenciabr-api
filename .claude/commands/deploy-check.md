---
description: Verifica se o projeto está pronto para deploy em produção
---

Invoque o subagent `deploy-checker` para validar prontidão de deploy.

O subagent executa checklist em 5 categorias:

- **A**. Sanidade do código (testes, lint, format, type check, cobertura)
- **B**. Configuração (.env, .env.example, SECRET_KEY, DEBUG, CORS)
- **C**. Segurança (segredos, histórico, CORS, deps, hashing)
- **D**. Infraestrutura (deps consistentes, Procfile/Dockerfile, Python version, migrations, health)
- **E**. Qualidade da entrega (README, CHANGELOG, CI verde, branch)

Cada check produz ✅, 🟡 ou ❌ com evidência.

## Veredito final esperado

- ✅ **PRONTO** — pode fazer deploy
- 🟡 **PRONTO COM RESSALVAS** — sem bloqueadores, mas com avisos
- ❌ **NÃO PRONTO** — bloqueadores presentes

## Após receber o relatório

Se ❌, apresente os bloqueadores ordenados por prioridade e pergunte:

```
Quer que eu corrija os bloqueadores um a um?
Ou prefere abordar manualmente?
```

Se ✅ ou 🟡, mostre o relatório e sugira:

```
Próximos passos para deploy:
1. Configurar variáveis no painel da plataforma (Railway/Render/Fly)
2. Conectar repositório
3. Fazer push para main → CI passa → deploy automático
4. Após deploy: testar /health no domínio público
5. Configurar monitoramento (Sentry, UptimeRobot)
```

Não execute o deploy automaticamente — apenas valide.