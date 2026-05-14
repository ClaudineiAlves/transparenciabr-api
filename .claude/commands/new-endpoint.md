---
description: Cria um endpoint completo (schema + service + router + teste) seguindo a arquitetura do projeto
---

Use a skill `create-endpoint` para criar um endpoint baseado em: $ARGUMENTS

Passos esperados:
1. Esclarecer requisito se houver ambiguidade (uma pergunta, no máximo)
2. Criar schema Pydantic em `app/schemas/`
3. Criar service em `app/services/`
4. Criar router em `app/api/`
5. Registrar router em `app/main.py`
6. Criar testes em `tests/`
7. Rodar `pytest`, `ruff check`, `ruff format` para validar
8. Sugerir mensagem de commit em Conventional Commits

Ao final, reporte:
- Arquivos criados/modificados
- Testes adicionados (quantos e quais cenários)
- Endpoint acessível em qual URL após `uvicorn app.main:app --reload`
- Próximos passos sugeridos (ex: adicionar autenticação, cache, etc.)