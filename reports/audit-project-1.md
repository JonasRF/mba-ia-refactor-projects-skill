# Architecture Audit Report

| | |
|---|---|
| **Project** | `code-smells-project` |
| **Stack** | Python + Flask 3.1.1 |
| **Files** | 4 analyzed · ~781 lines of code |
| **Date** | 2026-06-26 |

---

## Executive Summary

This report presents the findings of a static architecture review of the `code-smells-project` codebase. A total of **22 findings** were identified across 4 source files, including critical SQL injection vulnerabilities and exposed secrets — issues that represent immediate security risk in a production environment.

| Severity | Count | Status |
|:---|:---:|:---|
| 🔴 CRITICAL | 8 | Open |
| 🟠 HIGH | 5 | Open |
| 🟡 MEDIUM | 6 | Open |
| 🟢 LOW | 4 | Open |
| **Total** | **23** | |

---

## Findings

---

### 🔴 `AP-01` — God Class / Monolith File

| | |
|---|---|
| **File** | `app.py` |
| **Lines** | 47–78 |

```python
@app.route("/admin/reset-db", methods=["POST"])
def reset_database():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM itens_pedido")
    cursor.execute("DELETE FROM pedidos")
    cursor.execute("DELETE FROM produtos")
    cursor.execute("DELETE FROM usuarios")
    db.commit()
```

**Problem**

`app.py` concentra inicialização da aplicação, registro de rotas e handlers inline com acesso direto ao banco. As rotas `/admin/reset-db` e `/admin/query` executam lógica de persistência sem passar pelas camadas Model/Controller, violando completamente a separação de responsabilidades.

**Recommended Action**

Mover rotas admin para `routes/admin.py`; delegar acesso ao banco ao model layer. `app.py` deve conter apenas bootstrap e registro de blueprints.

---

### 🔴 `AP-02a` — Hardcoded Credentials / Secrets in Source

| | |
|---|---|
| **File** | `app.py` |
| **Lines** | 7–8 |

```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
```

**Problem**

A `SECRET_KEY` é um literal hardcoded diretamente no código-fonte. Qualquer commit expõe a chave no histórico git; repositórios públicos ou leaks de código comprometem toda a segurança de sessão.

**Recommended Action**

Substituir por variável de ambiente: `app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")`. Nunca comitar secrets reais.

---

### 🔴 `AP-02b` — Hardcoded Credentials / Secrets in Source

| | |
|---|---|
| **File** | `database.py` |
| **Lines** | 73–83 |

```python
usuarios = [
    ("Admin",         "admin@loja.com",  "admin123", "admin"),
    ("João Silva",    "joao@email.com",  "123456",   "cliente"),
    ("Maria Santos",  "maria@email.com", "senha123", "cliente"),
]
cursor.executemany(
    "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
    usuarios
)
```

**Problem**

Credenciais de usuários default com senhas em plaintext estão hardcoded na inicialização do banco. As senhas não são hasheadas e ficam expostas em qualquer acesso ao código-fonte ou ao arquivo `.db`.

**Recommended Action**

Remover seed data do código-fonte; usar script de seed separado (fora do versionamento) com senhas hasheadas via `bcrypt`/`argon2`. Nunca armazenar senhas em texto claro.

---

### 🔴 `AP-02c` — Hardcoded Credentials / Secrets in Source

| | |
|---|---|
| **File** | `controllers.py` |
| **Lines** | 285–290 |

```python
return jsonify({
    "status":     "ok",
    "database":   "connected",
    "versao":     "1.0.0",
    "ambiente":   "producao",
    "db_path":    "loja.db",
    "debug":      True,
    "secret_key": "minha-chave-super-secreta-123"
}), 200
```

**Problem**

A `SECRET_KEY` é explicitamente retornada no response do endpoint `/health`. Qualquer cliente HTTP — incluindo usuários não autenticados — pode obter a chave de assinatura de sessão, comprometendo completamente a segurança.

**Recommended Action**

Remover `secret_key`, `debug` e `db_path` do response. O health check deve retornar apenas status operacional (`status`, `database`, `versao`, `counts`).

---

### 🔴 `AP-03a` — SQL Injection (Concatenação Direta)

| | |
|---|---|
| **File** | `app.py` |
| **Lines** | 59–78 |

```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    dados = request.get_json()
    query = dados.get("sql", "")
    if not query:
        return jsonify({"erro": "Query não informada"}), 400
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query)
```

**Problem**

Endpoint aceita SQL arbitrário do usuário e o executa diretamente sem autenticação, sanitização ou restrição. É um backdoor completo: qualquer cliente pode executar `DROP TABLE`, `SELECT` de dados sensíveis, ou criar usuários admin.

**Recommended Action**

Remover este endpoint imediatamente. Se administração de banco for necessária, usar ferramentas CLI autenticadas (ex: `sqlite3` CLI restrito ao servidor).

---

### 🔴 `AP-03b` — SQL Injection (Concatenação Direta)

| | |
|---|---|
| **File** | `models.py` |
| **Lines** | 105–111 |

```python
cursor.execute(
    "SELECT * FROM usuarios WHERE email = '" + email +
    "' AND senha = '" + senha + "'"
)
```

**Problem**

A query de login é construída por concatenação de strings. Um atacante pode usar `' OR '1'='1` no campo `email` para bypass completo de autenticação, obtendo acesso como qualquer usuário.

**Recommended Action**

Usar query parametrizada:
```python
cursor.execute(
    "SELECT * FROM usuarios WHERE email = ? AND senha = ?",
    (email, senha_hash)
)
```
Também implementar hashing de senha.

---

### 🔴 `AP-03c` — SQL Injection (Concatenação Direta)

| | |
|---|---|
| **File** | `models.py` |
| **Lines** | 47–50 |

```python
cursor.execute(
    "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES ('"
    + nome + "', '" + descricao + "', "
    + str(preco) + ", " + str(estoque) + ", '" + categoria + "')"
)
```

**Problem**

Query `INSERT` construída por concatenação de `nome` e `descricao` permite injeção SQL via campos de texto. Um nome como `'); DROP TABLE produtos; --` destruiria a tabela.

**Recommended Action**

Usar placeholders:
```python
cursor.execute(
    "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
    (nome, descricao, preco, estoque, categoria)
)
```

---

### 🟠 `AP-04a` — Fat Controller — Criação de Pedido

| | |
|---|---|
| **File** | `models.py` |
| **Lines** | 133–169 |

```python
def criar_pedido(usuario_id, itens):
    ...
    for item in itens:
        cursor.execute("SELECT * FROM produtos WHERE id = " + str(item["produto_id"]))
        produto = cursor.fetchone()
        if produto is None:
            return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": "Estoque insuficiente para " + produto["nome"]}
        total = total + (produto["preco"] * item["quantidade"])
```

**Problem**

Validação de estoque, cálculo de total e orquestração de múltiplas entidades (`produtos`, `pedidos`, `itens_pedido`) vivem na camada Model. Models devem apenas persistir dados; regras de negócio pertencem a uma camada Service.

**Recommended Action**

Extrair para `PedidoService.criar_pedido(usuario_id, itens)`. O model deve expor apenas `PedidoModel.inserir(usuario_id, total)` e `ItemPedidoModel.inserir(pedido_id, produto_id, quantidade, preco)`.

---

### 🟠 `AP-04b` — Fat Controller — Relatório de Vendas

| | |
|---|---|
| **File** | `models.py` |
| **Lines** | 235–273 |

```python
def relatorio_vendas():
    ...
    desconto = 0
    if faturamento > 10000:
        desconto = faturamento * 0.1
    elif faturamento > 5000:
        desconto = faturamento * 0.05
    elif faturamento > 1000:
        desconto = faturamento * 0.02
    return {"faturamento_bruto": ..., "desconto_aplicavel": ..., ...}
```

**Problem**

Regras de negócio para cálculo de desconto progressivo (tiers de faturamento) estão implementadas na camada Model. Esta lógica é domain business logic e deve residir em uma Service ou camada de domínio.

**Recommended Action**

Extrair para `RelatorioService.calcular_desconto(faturamento) -> float`. O model deve apenas retornar os dados agregados brutos do banco.

---

### 🟠 `AP-04c` — Fat Controller — Side Effects no Controller

| | |
|---|---|
| **File** | `controllers.py` |
| **Lines** | 188–220 |

```python
resultado = models.criar_pedido(usuario_id, itens)
if "erro" in resultado:
    return jsonify({"erro": resultado["erro"], "sucesso": False}), 400
print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + " criado para usuario " + str(usuario_id))
print("ENVIANDO SMS: Seu pedido foi recebido!")
print("ENVIANDO PUSH: Novo pedido recebido pelo sistema")
```

**Problem**

Lógica de side-effects (email, SMS, push notification) está hardcoded no controller. O controller viola SRP ao assumir responsabilidade de notificação além de coordenar request/response.

**Recommended Action**

Extrair para `NotificacaoService.notificar_pedido_criado(pedido_id, usuario_id)`. Injetar o serviço no controller.

---

### 🟠 `AP-05` — Hard Coupling / No Dependency Injection

| | |
|---|---|
| **File** | `models.py` |
| **Lines** | 1–6 |

```python
from database import get_db
import sqlite3

def get_todos_produtos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos")
```

**Problem**

Todas as funções de model importam e chamam `get_db()` diretamente — acoplamento rígido ao singleton global de conexão. Impossível injetar conexão de teste ou mock do banco, tornando testes unitários inviáveis.

**Recommended Action**

Usar `Flask g` para conexão escopada por request; ou aceitar `db` como parâmetro nas funções de model para possibilitar injeção em testes.

---

### 🟠 `AP-06` — Global Mutable State

| | |
|---|---|
| **File** | `database.py` |
| **Lines** | 4–11 |

```python
db_connection = None
db_path = "loja.db"

def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(db_path, check_same_thread=False)
        db_connection.row_factory = sqlite3.Row
```

**Problem**

`db_connection` é uma variável global mutável compartilhada entre todas as requisições. O `check_same_thread=False` suprime a proteção nativa do `sqlite3`, expondo race conditions em servidor multi-thread. Uma conexão única para toda a aplicação também não libera recursos entre requests.

**Recommended Action**

Escopar conexão por request via Flask `g`:
```python
g.db = sqlite3.connect(...)
```
Com teardown:
```python
@app.teardown_appcontext
def close_db(e):
    g.pop("db", None).close()
```

---

### 🟡 `AP-07a` — N+1 Query Problem — Pedidos por Usuário

| | |
|---|---|
| **File** | `models.py` |
| **Lines** | 186–199 |

```python
cursor2 = db.cursor()
cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
itens = cursor2.fetchall()
for item in itens:
    cursor3 = db.cursor()
    cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
    prod = cursor3.fetchone()
```

**Problem**

Para cada pedido, uma query busca seus itens; para cada item, outra query busca o nome do produto. 10 pedidos com 5 itens cada = 61 queries (1 + 10 + 50). Performance degrada linearmente com volume.

**Recommended Action**

Substituir por JOIN único:
```sql
SELECT p.*, i.*, pr.nome
FROM pedidos p
JOIN itens_pedido i ON i.pedido_id = p.id
JOIN produtos pr    ON pr.id = i.produto_id
WHERE p.usuario_id = ?
```

---

### 🟡 `AP-07b` — N+1 Query Problem — Todos os Pedidos

| | |
|---|---|
| **File** | `models.py` |
| **Lines** | 218–232 |

```python
cursor2 = db.cursor()
cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
itens = cursor2.fetchall()
for item in itens:
    cursor3 = db.cursor()
    cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
    prod = cursor3.fetchone()
```

**Problem**

`get_todos_pedidos` replica o mesmo padrão N+1 de `get_pedidos_usuario`. Para toda a base de pedidos este padrão é catastrófico em produção — 1000 pedidos = milhares de queries por request.

**Recommended Action**

Usar JOIN abrangendo `pedidos`, `itens_pedido` e `produtos`. Extrair lógica de serialização para helper `_build_pedidos_com_itens(rows)` reutilizável pelas duas funções.

---

### 🟡 `AP-08a` — Missing Input Validation at Route Level

| | |
|---|---|
| **File** | `controllers.py` |
| **Lines** | 118–121 |

```python
if preco_min:
    preco_min = float(preco_min)
if preco_max:
    preco_max = float(preco_max)
```

**Problem**

`float()` em query string sem `try/except` lança `ValueError` se o cliente enviar um valor não-numérico (ex: `?preco_min=abc`), resultando em HTTP 500 com stack trace exposto.

**Recommended Action**

Envolver em bloco de tratamento:
```python
try:
    preco_min = float(preco_min)
except ValueError:
    return jsonify({"erro": "preco_min deve ser numérico"}), 400
```

---

### 🟡 `AP-08b` — Missing Input Validation at Route Level

| | |
|---|---|
| **File** | `controllers.py` |
| **Lines** | 237–241 |

```python
def atualizar_status_pedido(pedido_id):
    try:
        dados = request.get_json()
        novo_status = dados.get("status", "")
```

**Problem**

Se o request body for ausente, mal-formado ou `Content-Type` inválido, `request.get_json()` retorna `None` e `None.get(...)` lança `AttributeError` — HTTP 500 não tratado.

**Recommended Action**

Adicionar guarda antes de acessar campos do dict:
```python
if not dados:
    return jsonify({"erro": "Body JSON obrigatório"}), 400
```

---

### 🟡 `AP-09a` — Code Duplication / Missing DRY — Serialização de Produto

| | |
|---|---|
| **File** | `models.py` |
| **Lines** | 12–21, 30–40, 303–313 |

```python
result.append({
    "id":        row["id"],
    "nome":      row["nome"],
    "descricao": row["descricao"],
    "preco":     row["preco"],
    "estoque":   row["estoque"],
    "categoria": row["categoria"],
    "ativo":     row["ativo"],
    "criado_em": row["criado_em"]
})
```

**Problem**

O dict de serialização de produto é copiado identicamente em `get_todos_produtos`, `get_produto_por_id` e `buscar_produtos`. Qualquer campo novo ou renomeado exige alteração em 3 locais.

**Recommended Action**

Extrair para `def _serialize_produto(row) -> dict` e chamar nas três funções.

---

### 🟡 `AP-09b` — Code Duplication / Missing DRY — Serialização de Pedidos

| | |
|---|---|
| **File** | `models.py` |
| **Lines** | 171–233 |

```python
def get_pedidos_usuario(usuario_id):
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ...")
    # ~30 linhas de lógica de serialização com cursors aninhados

def get_todos_pedidos():
    cursor.execute("SELECT * FROM pedidos")
    # ~30 linhas idênticas de lógica de serialização com cursors aninhados
```

**Problem**

`get_pedidos_usuario` e `get_todos_pedidos` diferem apenas na cláusula `WHERE` mas compartilham ~30 linhas de lógica idêntica de serialização com cursors aninhados. Qualquer correção (ex: bug no N+1) deve ser aplicada em dois lugares.

**Recommended Action**

Extrair `_serialize_pedidos_com_itens(rows, db) -> list` e invocar de ambas as funções com apenas a query inicial diferente.

---

### 🟢 `AP-10a` — Magic Numbers and Magic Strings — Tiers de Desconto

| | |
|---|---|
| **File** | `models.py` |
| **Lines** | 256–259 |

```python
if faturamento > 10000:
    desconto = faturamento * 0.1
elif faturamento > 5000:
    desconto = faturamento * 0.05
elif faturamento > 1000:
    desconto = faturamento * 0.02
```

**Problem**

Os limiares de desconto (`10000`, `5000`, `1000`) e os multiplicadores (`0.1`, `0.05`, `0.02`) são magic numbers sem nome simbólico. Intenção e regra de negócio ficam obscurecidas; mudança de política exige caça manual no código.

**Recommended Action**

Definir constantes nomeadas em `config.py`:
```python
LIMITE_DESCONTO_ALTO   = 10_000;  TAXA_DESCONTO_ALTO   = 0.10
LIMITE_DESCONTO_MEDIO  =  5_000;  TAXA_DESCONTO_MEDIO  = 0.05
LIMITE_DESCONTO_BASICO =  1_000;  TAXA_DESCONTO_BASICO = 0.02
```

---

### 🟢 `AP-10b` — Magic Numbers and Magic Strings — Listas Inline

| | |
|---|---|
| **File** | `controllers.py` |
| **Lines** | 52–54, 242 |

```python
categorias_validas = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
...
if novo_status not in ["pendente", "aprovado", "enviado", "entregue", "cancelado"]:
```

**Problem**

Listas de categorias válidas e status válidos são magic strings inline em funções. Os mesmos valores provavelmente são necessários em validações, relatórios e testes, mas não há fonte única de verdade.

**Recommended Action**

Definir como constantes de módulo em `constants.py`:
```python
CATEGORIAS_VALIDAS = frozenset({"informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"})
STATUS_PEDIDO      = frozenset({"pendente", "aprovado", "enviado", "entregue", "cancelado"})
```

---

### 🟢 `AP-11a` — Poor Naming / Semantic Misalignment — Cursors

| | |
|---|---|
| **File** | `models.py` |
| **Lines** | 187, 219, 222, 225 |

```python
cursor2 = db.cursor()
cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
itens = cursor2.fetchall()
for item in itens:
    cursor3 = db.cursor()
    cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```

**Problem**

`cursor2` e `cursor3` são nomes sequenciais sem semântica. Ao ler o código não é possível identificar rapidamente qual cursor consulta itens e qual consulta produtos.

**Recommended Action**

Renomear para `itens_cursor` e `produto_cursor` respectivamente para comunicar intenção.

---

### 🟢 `AP-11b` — Poor Naming / Semantic Misalignment — Shadowing de Built-in

| | |
|---|---|
| **File** | `controllers.py` |
| **Lines** | 56, 160 |

```python
id = models.criar_produto(nome, descricao, preco, estoque, categoria)
...
id = models.criar_usuario(nome, email, senha)
```

**Problem**

`id` como nome de variável local sobrescreve a built-in `id()` do Python. Além de má prática, o nome é ambíguo quando múltiplas entidades são criadas no mesmo escopo.

**Recommended Action**

Renomear para `produto_id` e `usuario_id` respectivamente — mais descritivo e sem shadowing de built-in.

---

### 🔴 AP-14 — Fake or Predictable Authentication Token

| | |
|---|---|
| **File** | `routes/auth_routes.py` |
| **Lines** | 56, 160 |

```python
    dados = request.get_json(silent=True) or {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    try:
        usuario = UsuarioController.autenticar(email, senha)
        return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
    except PermissionError as e:
        return jsonify({"erro": str(e), "sucesso": False}), 401
```
        
**Problem**

O login não emite token algum — nem fake, nem assinado. `UsuarioController.autenticar`(controllers/usuario_controller.py:25-31) apenas retorna o dict do usuário em caso de sucesso. Nenhuma dependência de geração segura (`jwt`, `secrets.token_*`) é usada, enenhuma rota da aplicação (produtos, pedidos, usuários, relatórios) exige ou valida um header `Authorization`. Consequência: não existe autenticação real no sistema — qualquer cliente acessa e modifica qualquer recurso (criar/atualizar/deletar produtos, criar pedidos, listar usuários) sem se autenticar, e a resposta de "login OK" não estabelece nenhuma sessão verificável.

**Recommended Action**

Aplicar PT-13 do playbook — gerar um token assinado e expirável (JWT com `SECRET_KEY` do`app.config`, claims `sub`/`role`/`exp`) no login, e criar um decorator/middleware de autenticação que valide o header `Authorization` nas rotas que devem ser protegidas (ex.: criação/alteração de produtos e pedidos), retornando 401 quando ausente ou inválido.

----------------------------------------------------------------
