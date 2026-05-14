---
name: review-security
description: Revisa código Python/FastAPI procurando vulnerabilidades de segurança. Use ao revisar PRs antes de merge, antes de fazer deploy, após adicionar funcionalidades sensíveis (autenticação, upload, consultas externas), ou quando o usuário explicitamente pedir auditoria de segurança. Verifica injeção, autenticação, segredos, exposição de dados e dependências. Reporta achados em ordem de severidade com sugestão concreta de correção.
---

# Revisar segurança

Você está auditando código quanto a segurança. Sua função é encontrar problemas reais e propor correções concretas, não apenas listar diretrizes.

## Princípios da auditoria

1. **Severidade real** — diferencie crítico (exploitable agora) de baixo (boa prática). Não inflar nem subestimar.
2. **Evidência específica** — cite arquivo:linha e o trecho problemático.
3. **Correção acionável** — sempre sugira como consertar, com código quando possível.
4. **Sem teatro de segurança** — não recomende criptografia onde não há dado sensível, nem rate limit em endpoint público trivial.
5. **OWASP API Security Top 10** como referência mental (https://owasp.org/API-Security/).

## Formato do relatório

```
## 🔴 Crítico (bloqueia merge — pode ser explorado agora)
1. [arquivo:linha] Descrição clara do problema
   Impacto: o que um atacante pode fazer
   Correção: trecho de código corrigido

## 🟡 Importante (corrigir antes de produção)
2. ...

## 🟢 Sugestões (melhorias / defesa em profundidade)
3. ...

## ✅ Pontos positivos observados
- ...
```

Sempre inclua a seção de pontos positivos — reforça comportamentos certos.

## Checklist por categoria

Aplique cada categoria abaixo aos arquivos sob revisão. Use Grep/Read para buscar evidências.

### 1. Segredos e configuração

**Buscar:**
- Strings com aparência de chave/token: `[A-Za-z0-9_-]{20,}`
- Padrões: `password`, `api_key`, `secret`, `token`, `bearer`
- Atribuições suspeitas: `KEY = "..."`, `password="..."`

**Verificar:**
- [ ] Nenhum literal de API key, senha, token ou JWT secret no código
- [ ] Toda configuração sensível vem de `pydantic_settings` lendo `.env`
- [ ] `.env` está no `.gitignore`
- [ ] `.env.example` existe e NÃO contém valores reais
- [ ] `SECRET_KEY` tem pelo menos 32 bytes (`secrets.token_urlsafe(32)`)
- [ ] Logs não imprimem objetos completos de request (que podem ter Authorization header)

**Exemplo crítico:**

```python
# ❌ RUIM — chave no código
JWT_SECRET = "minha-chave-super-secreta-123"

# ✅ BOM — vem da config
from app.core.config import settings
JWT_SECRET = settings.secret_key
```

### 2. Autenticação

**Verificar em endpoints protegidos:**
- [ ] Usam `Depends(get_current_user)` ou equivalente
- [ ] `get_current_user` valida assinatura E expiração do JWT
- [ ] Algoritmo JWT explícito (não aceitar `none`): `jwt.decode(..., algorithms=["HS256"])`
- [ ] Hash de senha com `bcrypt` ou `argon2`, **nunca** SHA/MD5 puro
- [ ] Comparação de senha via biblioteca (constant-time): `bcrypt.checkpw`, não `==`
- [ ] Token expira em tempo razoável (15min-1h para access, 7-30d para refresh)
- [ ] Endpoint de login tem rate limit (mínimo 5/min por IP)
- [ ] Erro de senha errada e usuário inexistente retornam **mesma mensagem** (evita user enumeration)

**Exemplo crítico — algoritmo permissivo:**

```python
# ❌ CRÍTICO — aceita alg "none" se o atacante remover assinatura
payload = jwt.decode(token, SECRET_KEY)

# ✅ BOM — força algoritmo
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

**Exemplo crítico — user enumeration:**

```python
# ❌ RUIM — atacante descobre quais emails existem
if not user:
    raise HTTPException(404, "Usuário não encontrado")
if not bcrypt.checkpw(senha, user.password_hash):
    raise HTTPException(401, "Senha incorreta")

# ✅ BOM — mensagem genérica
if not user or not bcrypt.checkpw(senha, user.password_hash):
    raise HTTPException(401, "Credenciais inválidas")
```

### 3. Autorização

- [ ] Endpoints que acessam dados de usuário verificam que o usuário logado **é o dono** do recurso (IDOR/BOLA)
- [ ] Operações administrativas verificam role/permissão
- [ ] Não confiar em IDs vindos do cliente — sempre derivar do token

**Exemplo crítico — IDOR/BOLA (OWASP API #1):**

```python
# ❌ CRÍTICO — qualquer usuário lê os dados de qualquer outro
@router.get("/users/{user_id}/orders")
async def listar(user_id: int):
    return await orders.find(user_id=user_id)

# ✅ BOM — usa o usuário do token, ignora user_id da URL
@router.get("/me/orders")
async def listar(current_user: User = Depends(get_current_user)):
    return await orders.find(user_id=current_user.id)
```

### 4. Validação de entrada

- [ ] **Todo** parâmetro de query, path, body usa Pydantic
- [ ] `Field` com limites: `min_length`, `max_length`, `ge`, `le`, `pattern`
- [ ] Listas têm `max_length` para evitar payload bomba
- [ ] Strings que viram parte de paths/SQL/comandos têm whitelist de caracteres
- [ ] Datas como `date`/`datetime`, não `str`
- [ ] Enums para valores fechados (não validar strings livres se há lista finita)

**Exemplo crítico — sem limite de tamanho:**

```python
# ❌ RUIM — atacante envia 100MB de string
class Comment(BaseModel):
    text: str

# ✅ BOM
class Comment(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
```

### 5. Injeção (SQL, comando, path traversal)

**SQL Injection:**
- [ ] SQLAlchemy ORM usado corretamente (sem `text()` com f-string)
- [ ] Se usar SQL bruto, parâmetros nomeados: `text("WHERE id = :id")` + bind
- [ ] **Nunca** concatenar input do usuário em strings SQL

**Path Traversal:**
- [ ] Caminhos vindos de input validados com `pathlib.Path` e `.resolve()`
- [ ] Verificar se caminho final está dentro do diretório esperado

**Command Injection:**
- [ ] `subprocess` com `shell=False` e lista de args (nunca `shell=True` com input)
- [ ] Não use `os.system` com input do usuário

**Exemplos:**

```python
# ❌ CRÍTICO — SQL injection
query = f"SELECT * FROM users WHERE name = '{nome}'"
session.execute(text(query))

# ✅ BOM
session.execute(
    text("SELECT * FROM users WHERE name = :nome"),
    {"nome": nome},
)

# ❌ CRÍTICO — path traversal
arquivo = open(f"/uploads/{filename}")

# ✅ BOM
base = Path("/uploads").resolve()
caminho = (base / filename).resolve()
if not caminho.is_relative_to(base):
    raise HTTPException(400, "Path inválido")
```

### 6. CORS e headers

- [ ] `allow_origins` é lista específica, **nunca** `["*"]` com `allow_credentials=True`
- [ ] `allow_methods` lista apenas métodos usados
- [ ] Em produção: headers `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`
- [ ] CSP configurada se houver HTML servido

**Exemplo crítico:**

```python
# ❌ CRÍTICO — qualquer origem pode roubar sessão
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # FATAL combinado com *
)

# ✅ BOM
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # lista específica
    allow_credentials=True,
    allow_methods=["GET", "POST"],
)
```

### 7. Exposição de dados sensíveis

- [ ] Schemas de resposta NÃO contêm: hash de senha, salt, tokens, dados de outros usuários
- [ ] Mensagens de erro em produção NÃO contêm: stack trace, paths de arquivo, queries SQL, versões de software
- [ ] `debug=False` em produção (FastAPI esconde detalhes)
- [ ] Logs aplicam filtro/redação para campos sensíveis

**Exemplo:**

```python
# ❌ RUIM — schema retorna password_hash
class UserResponse(BaseModel):
    id: int
    email: str
    password_hash: str   # NUNCA

# ✅ BOM — campo sequer existe no response
class UserResponse(BaseModel):
    id: int
    email: str
```

### 8. Rate limiting e abuso

- [ ] Endpoints de login/registro: rate limit por IP (5/min)
- [ ] Endpoints de busca pesada: rate limit por usuário
- [ ] API externa cara (Portal da Transparência): cache + circuit breaker
- [ ] Limite global de tamanho de request (default do uvicorn é razoável)

### 9. Dependências e supply chain

- [ ] `pyproject.toml` fixa versões com `>=` mínimo de segurança
- [ ] Sem dependências de fontes não-oficiais (git URLs aleatórias)
- [ ] Dependabot ativo no GitHub
- [ ] Rodar `pip-audit` ou `safety check` periodicamente

```bash
pip install pip-audit
pip-audit
```

### 10. Específico do Portal da Transparência

- [ ] Chave da API SOMENTE no backend, nunca exposta no HTML/JS
- [ ] Cache reduz chamadas à API externa (respeita rate limit deles)
- [ ] Erros 429 do upstream tratados com backoff
- [ ] Timeout configurado em todas as chamadas (sem await infinito)
- [ ] Resposta da API externa NUNCA passada direto ao cliente sem validação/normalização (eles podem retornar campos novos que viram parte do nosso contrato sem querer)

## Ferramentas automatizadas para complementar

Antes de revisar manualmente, rode:

```bash
# Lint com regras de segurança (Bandit via Ruff)
ruff check --select S .

# Buscar segredos no histórico do Git
gitleaks detect --source . --verbose

# Auditoria de dependências
pip-audit
# ou
safety check

# Buscar padrões manualmente
grep -rn -iE "(api[_-]?key|secret|password|token)\s*=\s*['\"]" app/ tests/
grep -rn "shell=True" app/
grep -rn "eval\|exec\(" app/
```

## Processo da revisão

1. Liste arquivos modificados (ou todo o repo se for auditoria completa)
2. Para cada arquivo, aplique o checklist relevante
3. Rode as ferramentas automatizadas
4. Compile achados no formato do relatório
5. Priorize: crítico → importante → sugestões
6. Inclua pontos positivos
7. Termine com checklist de próximos passos para o autor

## Quando NÃO bloquear merge

- Sugestões de defesa em profundidade que não exploram nada agora
- Refatorações de organização (a menos que escondam um bug)
- "Daqui a 6 meses pode ser problema" — abra issue separada

## Quando bloquear ABSOLUTAMENTE

- Credenciais commitadas
- SQL injection
- Autenticação que não verifica assinatura
- IDOR/BOLA permitindo acesso a dados de outros
- CORS `*` + credentials
- Comando injection
- Stack traces vazando em produção

## Após a revisão

Sugira:
- Adicionar teste que reproduziria a vulnerabilidade
- Atualizar CLAUDE.md se descobriu um padrão novo
- Criar issue de "Security: ..." se há trabalho de defesa em profundidade pendente