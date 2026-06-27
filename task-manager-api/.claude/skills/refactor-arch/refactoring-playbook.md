# Refactoring Playbook — Phase 3 Reference

Este arquivo define os **padrões concretos de transformação** usados pela skill `refactor-arch`
na **Fase 3 (Refatoração)**. Para cada anti-pattern detectado na Fase 2 existe um padrão
correspondente aqui, com código ANTES e DEPOIS e os passos exatos da transformação.

Os exemplos são em Python/Flask (stack de referência), mas os princípios aplicam-se a qualquer
stack. Combine sempre com `architecture_guidelines.md` para garantir que o destino de cada
trecho de código é a camada correta.

> **Como usar:** localize o ID do anti-pattern (AP-01, AP-02…) encontrado no relatório de
> auditoria, aplique os passos de transformação na ordem indicada e valide com o checklist
> ao final de cada padrão.

---

## Sumário de Padrões

| Padrão | Anti-Pattern | Severidade | Transformação |
|--------|-------------|------------|---------------|
| [PT-01](#pt-01--god-file--blueprint-layered) | AP-01 God Class / Monolith File | CRITICAL | Decompor em Blueprints + camadas |
| [PT-02](#pt-02--hardcoded-secrets--env-vars) | AP-02 Hardcoded Credentials | CRITICAL | Mover para variáveis de ambiente |
| [PT-03](#pt-03--sql-injection--parameterized-queries) | AP-03 SQL Injection | CRITICAL | Substituir concatenação por placeholders |
| [PT-04](#pt-04--fat-controller--thin-controller--service) | AP-04 Fat Controller | HIGH | Extrair lógica para Controller/Service |
| [PT-05](#pt-05--hard-coupling--dependency-injection) | AP-05 Hard Coupling | HIGH | Introduzir abstrações e injeção |
| [PT-06](#pt-06--global-mutable-state--request-scoped-connection) | AP-06 Global Mutable State | HIGH | Escopo de conexão por request com flask.g |
| [PT-07](#pt-07--n1-query--join) | AP-07 N+1 Query | MEDIUM | Substituir loop de queries por JOIN |
| [PT-08](#pt-08--missing-validation--schema-validation) | AP-08 Missing Validation | MEDIUM | Adicionar validação na camada Routes |
| [PT-09](#pt-09--code-duplication--dry-extraction) | AP-09 Code Duplication | MEDIUM | Extrair funções e schemas reutilizáveis |
| [PT-10](#pt-10--magic-numbers--named-constants) | AP-10 Magic Numbers/Strings | LOW | Substituir por constantes nomeadas |
| [PT-11](#pt-11--poor-naming--semantic-rename) | AP-11 Poor Naming | LOW | Renomear para nomes semânticos |

---

## PT-01 — God File → Blueprint + Layered

**Anti-pattern:** AP-01 · **Severidade:** CRITICAL
**Trigger:** arquivo único mistura inicialização, rotas e acesso direto a banco.

### ANTES

```python
# app.py — mistura tudo
from flask import Flask, jsonify, request
from database import get_db
import controllers

app = Flask(__name__)
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
CORS(app)

# registro de rotas direto no app
app.add_url_rule("/produtos", "listar_produtos", controllers.listar_produtos, methods=["GET"])

# handler com acesso direto a banco no mesmo arquivo de bootstrap
@app.route("/admin/reset-db", methods=["POST"])
def reset_database():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM itens_pedido")
    cursor.execute("DELETE FROM pedidos")
    db.commit()
    return jsonify({"mensagem": "Banco resetado"}), 200

@app.route("/admin/query", methods=["POST"])
def executar_query():
    dados = request.get_json()
    query = dados.get("sql", "")
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query)          # SQL arbitrário sem autenticação
    return jsonify({"sucesso": True}), 200
```

### DEPOIS

```python
# app.py — apenas bootstrap
import os
from flask import Flask
from flask_cors import CORS
from database.connection import init_app
from routes.produto_routes import produto_bp
from routes.usuario_routes import usuario_bp
from routes.pedido_routes import pedido_bp

def create_app(config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
    app.config["DATABASE"]   = os.environ.get("DATABASE_PATH", "loja.db")
    app.config["DEBUG"]      = os.environ.get("FLASK_DEBUG", "false") == "true"

    if config:
        app.config.update(config)

    CORS(app)
    init_app(app)

    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(pedido_bp)

    return app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000)
```

```python
# routes/produto_routes.py — Blueprint isolado
from flask import Blueprint, request, jsonify
from controllers.produto_controller import ProdutoController

produto_bp = Blueprint("produtos", __name__, url_prefix="/produtos")

@produto_bp.get("/")
def listar_produtos():
    return jsonify({"dados": ProdutoController.listar(), "sucesso": True}), 200
```

### Passos de transformação

1. Criar `routes/<entidade>_routes.py` com um `Blueprint` para cada grupo de endpoints.
2. Mover cada `add_url_rule` / `@app.route` para o Blueprint correspondente.
3. Remover endpoints `/admin/reset-db` e `/admin/query` — não têm substituto em produção.
4. Reduzir `app.py` a uma função `create_app()` que apenas registra Blueprints e extensões.
5. Confirmar que `app.py` não importa `get_db`, `cursor` ou `models`.

### Checklist

- [ ] `app.py` contém apenas `create_app()` + `register_blueprint()`
- [ ] Nenhum `@app.route` ou `add_url_rule` em `app.py`
- [ ] Endpoints `/admin/query` e `/admin/reset-db` removidos
- [ ] Cada Blueprint tem seu próprio arquivo em `routes/`

---

## PT-02 — Hardcoded Secrets → Env Vars

**Anti-pattern:** AP-02 · **Severidade:** CRITICAL
**Trigger:** string literal atribuída a `SECRET_KEY`, `senha`, `password`, `token`; credencial
exposta em resposta de API.

### ANTES

```python
# app.py
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True

# database.py — senhas em texto plano no seed
usuarios = [
    ("Admin", "admin@loja.com", "admin123", "admin"),
    ("João",  "joao@email.com", "123456",   "cliente"),
]

# controllers.py — secret_key exposta na resposta
return jsonify({
    "status": "ok",
    "secret_key": "minha-chave-super-secreta-123"
}), 200
```

### DEPOIS

```python
# .env.example  (versionado — sem valores reais)
SECRET_KEY=
DATABASE_PATH=loja.db
FLASK_DEBUG=false

# .env  (NÃO versionado — adicionado ao .gitignore)
SECRET_KEY=<gere com: python -c "import secrets; print(secrets.token_hex(32))">
DATABASE_PATH=loja.db
FLASK_DEBUG=false
```

```python
# app.py
import os
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]   # KeyError se ausente = falha rápida
app.config["DEBUG"]      = os.environ.get("FLASK_DEBUG", "false") == "true"
```

```python
# database/connection.py — seed com senha hasheada
import bcrypt

def _seed_usuarios(cursor):
    usuarios = [
        ("Admin", "admin@loja.com", bcrypt.hashpw(b"admin123", bcrypt.gensalt()), "admin"),
        ("João",  "joao@email.com", bcrypt.hashpw(b"123456",   bcrypt.gensalt()), "cliente"),
    ]
    cursor.executemany(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)", usuarios
    )
```

```python
# routes/health_routes.py — health check sem dados sensíveis
@health_bp.get("/health")
def health_check():
    db = get_db()
    db.execute("SELECT 1")
    return jsonify({"status": "ok", "database": "connected"}), 200
```

### Passos de transformação

1. Criar `.env.example` com todas as variáveis necessárias (sem valores reais).
2. Adicionar `.env` ao `.gitignore`.
3. Substituir toda string literal de credencial por `os.environ["VAR"]`.
4. Instalar `bcrypt` (`pip install bcrypt`) e hashar senhas no seed.
5. Remover qualquer campo sensível (`secret_key`, `db_path`, `debug`) das respostas de API.
6. Verificar no histórico git se alguma credencial real já foi comitada — se sim, rotacionar.

### Checklist

- [ ] `.env` está no `.gitignore`
- [ ] `.env.example` está versionado com campos vazios
- [ ] `os.environ["SECRET_KEY"]` — sem fallback de string literal
- [ ] Senhas do seed armazenadas com hash
- [ ] Nenhuma resposta de API contém credencial, caminho de arquivo ou flag `debug`

---

## PT-03 — SQL Injection → Parameterized Queries

**Anti-pattern:** AP-03 · **Severidade:** CRITICAL
**Trigger:** `cursor.execute(` com `+`, `%`, `f"` ou interpolação de variável de request.

### ANTES

```python
# models.py — login com concatenação (authentication bypass)
cursor.execute(
    "SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"
)

# models.py — INSERT com concatenação
cursor.execute(
    "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES ('" +
    nome + "', '" + descricao + "', " + str(preco) + ", " + str(estoque) + ", '" + categoria + "')"
)

# models.py — query dinâmica de busca
query = "SELECT * FROM produtos WHERE 1=1"
if termo:
    query += " AND (nome LIKE '%" + termo + "%' OR descricao LIKE '%" + termo + "%')"
if categoria:
    query += " AND categoria = '" + categoria + "'"
cursor.execute(query)
```

### DEPOIS

```python
# models/usuario.py — login parametrizado
cursor.execute(
    "SELECT * FROM usuarios WHERE email = ? AND senha_hash = ?",
    (email, senha_hash)          # senha_hash = bcrypt.checkpw resultado
)

# models/produto.py — INSERT parametrizado
cursor.execute(
    "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
    (nome, descricao, preco, estoque, categoria)
)

# models/produto.py — query dinâmica segura
def buscar(termo=None, categoria=None, preco_min=None, preco_max=None) -> list[dict]:
    sql    = "SELECT * FROM produtos WHERE 1=1"
    params = []

    if termo:
        sql += " AND (nome LIKE ? OR descricao LIKE ?)"
        params += [f"%{termo}%", f"%{termo}%"]
    if categoria:
        sql += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        sql += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        sql += " AND preco <= ?"
        params.append(preco_max)

    cursor.execute(sql, params)
    return [_row_to_dict(row) for row in cursor.fetchall()]
```

### Passos de transformação

1. Localizar **todo** `cursor.execute(` que contenha `+` ou `f"` com variável externa.
2. Extrair os valores para uma tupla `params`.
3. Substituir cada valor interpolado por `?` na string SQL.
4. Passar `params` como segundo argumento: `cursor.execute(sql, params)`.
5. Para queries dinâmicas, acumular cláusulas e parâmetros em listas separadas e juntar no final.
6. Nunca usar `str.format()` ou f-strings em strings SQL.

### Checklist

- [ ] Zero ocorrências de `" + variavel` ou `f"...{variavel}` dentro de strings SQL
- [ ] Todo `cursor.execute(` tem segundo argumento `(params,)` ou `[]`
- [ ] Query dinâmica de busca usa lista `params` acumulada
- [ ] Login valida senha com `bcrypt.checkpw` — não compara texto plano em SQL

---

## PT-04 — Fat Controller → Thin Controller + Service

**Anti-pattern:** AP-04 · **Severidade:** HIGH
**Trigger:** função de controller com >30 linhas; regras de negócio, cálculos ou side-effects
(email, SMS, notificações) dentro de handler HTTP.

### ANTES

```python
# controllers.py — validação de domínio + notificações inline no handler HTTP
def criar_pedido():
    dados = request.get_json()
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        return jsonify({"erro": "Usuario ID é obrigatório"}), 400
    if not itens or len(itens) == 0:
        return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

    resultado = models.criar_pedido(usuario_id, itens)

    # side-effects de notificação inline — violação de SRP
    print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + " criado")
    print("ENVIANDO SMS: Seu pedido foi recebido!")
    print("ENVIANDO PUSH: Novo pedido recebido pelo sistema")

    return jsonify({"dados": resultado, "sucesso": True}), 201
```

### DEPOIS

```python
# controllers/pedido_controller.py — apenas orquestração de domínio
from models.pedido import PedidoModel
from services.notification_service import NotificationService

class PedidoController:

    def __init__(self, notifier: NotificationService = None):
        self.notifier = notifier or NotificationService()

    def criar(self, usuario_id: int, itens: list[dict]) -> dict:
        if not usuario_id:
            raise ValueError("usuario_id é obrigatório")
        if not itens:
            raise ValueError("Pedido deve ter pelo menos 1 item")

        resultado = PedidoModel.criar(usuario_id, itens)

        self.notifier.pedido_criado(
            pedido_id=resultado["pedido_id"],
            usuario_id=usuario_id
        )
        return resultado
```

```python
# services/notification_service.py — side-effects isolados
class NotificationService:

    def pedido_criado(self, pedido_id: int, usuario_id: int) -> None:
        # aqui vai a integração real (SMTP, Twilio, Firebase, etc.)
        print(f"[EMAIL] Pedido {pedido_id} criado para usuário {usuario_id}")
        print(f"[SMS]   Seu pedido {pedido_id} foi recebido!")
        print(f"[PUSH]  Novo pedido {pedido_id} no sistema")

    def pedido_status_atualizado(self, pedido_id: int, novo_status: str) -> None:
        if novo_status == "aprovado":
            print(f"[EMAIL] Pedido {pedido_id} aprovado — preparar envio")
        elif novo_status == "cancelado":
            print(f"[EMAIL] Pedido {pedido_id} cancelado — devolver estoque")
```

```python
# routes/pedido_routes.py — handler HTTP limpo
from flask import Blueprint, request, jsonify
from controllers.pedido_controller import PedidoController

pedido_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")
_controller = PedidoController()

@pedido_bp.post("/")
def criar_pedido():
    dados = request.get_json(silent=True) or {}
    try:
        resultado = _controller.criar(
            usuario_id=dados.get("usuario_id"),
            itens=dados.get("itens", [])
        )
        return jsonify({"dados": resultado, "sucesso": True}), 201
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400
```

### Passos de transformação

1. Identificar todo bloco de negócio no handler (validações de domínio, cálculos, notificações).
2. Criar `controllers/<entidade>_controller.py` com classe e métodos estáticos ou de instância.
3. Mover regras de domínio para o Controller; converter retornos de erro para `raise ValueError`.
4. Criar `services/notification_service.py` e mover todo `print("ENVIANDO...")` para lá.
5. O handler HTTP fica com: parse → chamar controller → capturar exceção → retornar JSON.

### Checklist

- [ ] Nenhuma função de route tem mais de 20 linhas
- [ ] Nenhum `print("ENVIANDO...")` em routes ou controllers
- [ ] `NotificationService` tem métodos nomeados por evento de negócio
- [ ] Exceções de domínio levantadas no Controller, capturadas na Route

---

## PT-05 — Hard Coupling → Dependency Injection

**Anti-pattern:** AP-05 · **Severidade:** HIGH
**Trigger:** `import` direto de módulo de infraestrutura dentro de camada de negócio; ausência de
interfaces ou protocolos; singleton global importado por todos os módulos.

### ANTES

```python
# models.py — importa get_db diretamente, sem abstração
from database import get_db

def get_todos_produtos():
    db = get_db()          # acoplado à implementação concreta
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos")
    ...

# controllers.py — importa models e database diretamente
import models
from database import get_db

def health_check():
    db = get_db()          # controller acessando banco diretamente
    cursor = db.cursor()
    cursor.execute("SELECT 1")
    ...
```

### DEPOIS

```python
# database/connection.py — contrato explícito via Protocol
from typing import Protocol

class DatabaseProtocol(Protocol):
    def cursor(self): ...
    def commit(self): ...
    def close(self): ...

def get_db() -> DatabaseProtocol:
    ...  # implementação com flask.g (ver PT-06)
```

```python
# models/produto.py — recebe conexão como parâmetro (injeção simples)
from database.connection import get_db

class ProdutoModel:

    @staticmethod
    def get_todos(db=None) -> list[dict]:
        conn = db or get_db()          # permite injeção em testes
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos")
        return [ProdutoModel._row_to_dict(r) for r in cursor.fetchall()]
```

```python
# controllers/produto_controller.py — depende de abstração, não de implementação
from models.produto import ProdutoModel

class ProdutoController:

    def __init__(self, model=None):
        self.model = model or ProdutoModel   # injetável em testes

    def listar(self) -> list[dict]:
        return self.model.get_todos()
```

```python
# routes/health_routes.py — health check sem acesso direto ao banco
from flask import Blueprint, jsonify
from models.produto import ProdutoModel

health_bp = Blueprint("health", __name__)

@health_bp.get("/health")
def health_check():
    contagens = {
        "produtos": len(ProdutoModel.get_todos()),
    }
    return jsonify({"status": "ok", "counts": contagens}), 200
```

### Passos de transformação

1. Criar `DatabaseProtocol` (Protocol/ABC) em `database/connection.py`.
2. Adicionar parâmetro `db=None` nos métodos de Model — usa `get_db()` como default.
3. Adicionar parâmetro `model=None` nos Controllers — usa classe concreta como default.
4. Remover `from database import get_db` de `controllers/` e `routes/`.
5. Em testes, injetar conexão em memória: `ProdutoModel.get_todos(db=sqlite3.connect(":memory:"))`.

### Checklist

- [ ] Nenhum arquivo em `controllers/` importa `get_db` diretamente
- [ ] Nenhum arquivo em `routes/` importa `get_db` diretamente
- [ ] Models aceitam `db` como parâmetro opcional
- [ ] Controllers aceitam `model` como parâmetro opcional

---

## PT-06 — Global Mutable State → Request-Scoped Connection

**Anti-pattern:** AP-06 · **Severidade:** HIGH
**Trigger:** variável global `db_connection = None` modificada por `global`; `check_same_thread=False`
sem justificativa; conexão compartilhada entre threads.

### ANTES

```python
# database.py
import sqlite3

db_connection = None          # estado global mutável

def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect("loja.db", check_same_thread=False)
        db_connection.row_factory = sqlite3.Row
    return db_connection      # mesma conexão para todas as threads
```

### DEPOIS

```python
# database/connection.py
import sqlite3
import flask

def get_db():
    if "db" not in flask.g:                      # flask.g é local por request
        flask.g.db = sqlite3.connect(
            flask.current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        flask.g.db.row_factory = sqlite3.Row
    return flask.g.db

def close_db(e=None):
    db = flask.g.pop("db", None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)   # fecha conexão ao fim de cada request
    _create_schema(app)

def _create_schema(app):
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS produtos (...);
            CREATE TABLE IF NOT EXISTS usuarios (...);
            CREATE TABLE IF NOT EXISTS pedidos (...);
            CREATE TABLE IF NOT EXISTS itens_pedido (...);
        """)
        db.commit()
```

### Passos de transformação

1. Remover `db_connection = None` e `global db_connection` de `database.py`.
2. Substituir por `flask.g` — cada request recebe sua própria conexão.
3. Remover `check_same_thread=False` — não é mais necessário.
4. Registrar `teardown_appcontext(close_db)` via `init_app(app)`.
5. Chamar `init_app(app)` dentro de `create_app()` em `app.py`.
6. Remover criação de schema e seed do corpo de `get_db()` — mover para `_create_schema`.

### Checklist

- [ ] Zero ocorrências de `global db_connection`
- [ ] `flask.g.db` usado para escopar conexão por request
- [ ] `teardown_appcontext(close_db)` registrado
- [ ] `check_same_thread=False` removido
- [ ] Schema criado em `_create_schema()` separado, chamado uma vez na inicialização

---

## PT-07 — N+1 Query → JOIN

**Anti-pattern:** AP-07 · **Severidade:** MEDIUM
**Trigger:** `cursor.execute(` dentro de `for` iterando sobre rows; cursores auxiliares (`cursor2`,
`cursor3`) dentro de loops.

### ANTES

```python
# models.py — N+1: 1 query de pedidos + N de itens + N×M de produto
def get_pedidos_usuario(usuario_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = " + str(usuario_id))
    rows = cursor.fetchall()
    result = []
    for row in rows:
        pedido = {"id": row["id"], "itens": []}
        cursor2 = db.cursor()
        cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
        itens = cursor2.fetchall()
        for item in itens:
            cursor3 = db.cursor()
            cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
            prod = cursor3.fetchone()
            pedido["itens"].append({"produto_nome": prod["nome"]})
        result.append(pedido)
    return result
```

### DEPOIS

```python
# models/pedido.py — 1 query com JOIN resolve tudo
def get_por_usuario(usuario_id: int) -> list[dict]:
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            p.id          AS pedido_id,
            p.usuario_id,
            p.status,
            p.total,
            p.criado_em,
            ip.produto_id,
            ip.quantidade,
            ip.preco_unitario,
            pr.nome       AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
        LEFT JOIN produtos      pr ON pr.id = ip.produto_id
        WHERE p.usuario_id = ?
        ORDER BY p.id, ip.id
    """, (usuario_id,))

    return _agrupar_pedidos(cursor.fetchall())

def _agrupar_pedidos(rows: list) -> list[dict]:
    pedidos: dict[int, dict] = {}
    for row in rows:
        pid = row["pedido_id"]
        if pid not in pedidos:
            pedidos[pid] = {
                "id":         pid,
                "usuario_id": row["usuario_id"],
                "status":     row["status"],
                "total":      row["total"],
                "criado_em":  row["criado_em"],
                "itens":      []
            }
        if row["produto_id"]:
            pedidos[pid]["itens"].append({
                "produto_id":     row["produto_id"],
                "produto_nome":   row["produto_nome"],
                "quantidade":     row["quantidade"],
                "preco_unitario": row["preco_unitario"]
            })
    return list(pedidos.values())
```

### Passos de transformação

1. Identificar toda query dentro de loop (`for row in rows: cursor.execute(...)`).
2. Mapear as tabelas envolvidas e seus relacionamentos (FK).
3. Escrever um único SELECT com `JOIN` cobrindo todas as tabelas necessárias.
4. Extrair função `_agrupar_<entidade>(rows)` para reagrupar o resultado flat em estrutura aninhada.
5. Reutilizar `_agrupar_pedidos` em `get_por_usuario` e `get_todos` — resolve AP-09 junto.
6. Remover todos os `cursor2`, `cursor3` e cursores auxiliares dentro de loops.

### Checklist

- [ ] Zero `cursor.execute(` dentro de blocos `for`
- [ ] `cursor2` e `cursor3` não existem mais
- [ ] JOIN cobre pedidos + itens_pedido + produtos em uma query
- [ ] `_agrupar_pedidos` reutilizado em todas as funções de listagem

---

## PT-08 — Missing Validation → Schema Validation

**Anti-pattern:** AP-08 · **Severidade:** MEDIUM
**Trigger:** `float(request.args.get(...))` ou `int(dados["campo"])` sem try/except; ausência de
biblioteca de validação; campos obrigatórios verificados com `if not campo`.

### ANTES

```python
# controllers.py — conversão sem tratamento de erro de tipo
def buscar_produtos():
    termo      = request.args.get("q", "")
    categoria  = request.args.get("categoria", None)
    preco_min  = request.args.get("preco_min", None)
    preco_max  = request.args.get("preco_max", None)

    if preco_min:
        preco_min = float(preco_min)   # ValueError se "abc" — retorna 500
    if preco_max:
        preco_max = float(preco_max)   # idem

    resultados = models.buscar_produtos(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados}), 200
```

### DEPOIS (validação manual na camada Routes)

```python
# routes/produto_routes.py — parse e validação de tipo na Route
from flask import Blueprint, request, jsonify
from controllers.produto_controller import ProdutoController

produto_bp = Blueprint("produtos", __name__, url_prefix="/produtos")

def _parse_float(valor, nome_campo: str) -> float | None:
    if valor is None:
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"'{nome_campo}' deve ser um número válido, recebido: '{valor}'")

@produto_bp.get("/busca")
def buscar_produtos():
    try:
        preco_min = _parse_float(request.args.get("preco_min"), "preco_min")
        preco_max = _parse_float(request.args.get("preco_max"), "preco_max")
    except ValueError as e:
        return jsonify({"erro": str(e)}), 400

    resultados = ProdutoController.buscar(
        termo=request.args.get("q", ""),
        categoria=request.args.get("categoria"),
        preco_min=preco_min,
        preco_max=preco_max
    )
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
```

### DEPOIS (opcional — com Pydantic para validação declarativa)

```python
# routes/produto_routes.py — validação declarativa com Pydantic
from pydantic import BaseModel, Field, field_validator

class BuscaProdutoParams(BaseModel):
    q:         str   = ""
    categoria: str | None = None
    preco_min: float | None = Field(None, ge=0)
    preco_max: float | None = Field(None, ge=0)

@produto_bp.get("/busca")
def buscar_produtos():
    try:
        params = BuscaProdutoParams(**request.args.to_dict())
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

    resultados = ProdutoController.buscar(**params.model_dump())
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
```

### Passos de transformação

1. Localizar todo `int(...)` e `float(...)` sem try/except em handlers de rota.
2. Extrair funções auxiliares de parse: `_parse_float`, `_parse_int` com mensagens de erro claras.
3. Envolver chamadas de parse em try/except ValueError → retornar 400.
4. Para projetos novos ou com Pydantic disponível: definir schema de request e usar `.model_dump()`.
5. Garantir que ValueError do Controller também é capturado na Route e retorna 400.

### Checklist

- [ ] Zero `float(request.args.get(...))` sem try/except
- [ ] Zero `int(dados["campo"])` sem try/except
- [ ] Erro de tipo retorna 400 com mensagem legível, não 500 com stack trace
- [ ] Stack traces nunca chegam ao cliente

---

## PT-09 — Code Duplication → DRY Extraction

**Anti-pattern:** AP-09 · **Severidade:** MEDIUM
**Trigger:** mesmo bloco de validação copiado em 2+ funções; mesma serialização de objeto em
2+ lugares; mesma lógica de fetch repetida em funções quase idênticas.

### ANTES

```python
# controllers.py — validação duplicada em criar e atualizar produto
def criar_produto():
    dados = request.get_json()
    if "nome" not in dados:
        return jsonify({"erro": "Nome é obrigatório"}), 400
    if "preco" not in dados:
        return jsonify({"erro": "Preço é obrigatório"}), 400
    if "estoque" not in dados:
        return jsonify({"erro": "Estoque é obrigatório"}), 400
    # ... 15 linhas de validação

def atualizar_produto(id):
    dados = request.get_json()
    if "nome" not in dados:
        return jsonify({"erro": "Nome é obrigatório"}), 400    # cópia
    if "preco" not in dados:
        return jsonify({"erro": "Preço é obrigatório"}), 400   # cópia
    if "estoque" not in dados:
        return jsonify({"erro": "Estoque é obrigatório"}), 400 # cópia
    # ... mesmas 15 linhas
```

### DEPOIS

```python
# routes/produto_routes.py — helper de parse centralizado
def _parse_produto_body(dados: dict) -> dict:
    campos = ["nome", "preco", "estoque"]
    for campo in campos:
        if campo not in dados:
            raise ValueError(f"Campo obrigatório ausente: {campo}")
    return {
        "nome":      str(dados["nome"]),
        "descricao": str(dados.get("descricao", "")),
        "preco":     float(dados["preco"]),
        "estoque":   int(dados["estoque"]),
        "categoria": str(dados.get("categoria", "geral")),
    }

@produto_bp.post("/")
def criar_produto():
    dados = request.get_json(silent=True) or {}
    try:
        campos = _parse_produto_body(dados)
        resultado = ProdutoController.criar(**campos)
        return jsonify({"dados": resultado, "sucesso": True}), 201
    except (TypeError, ValueError) as e:
        return jsonify({"erro": str(e)}), 400

@produto_bp.put("/<int:produto_id>")
def atualizar_produto(produto_id):
    dados = request.get_json(silent=True) or {}
    try:
        campos = _parse_produto_body(dados)     # reutiliza o mesmo helper
        ProdutoController.atualizar(produto_id, **campos)
        return jsonify({"sucesso": True}), 200
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404
    except (TypeError, ValueError) as e:
        return jsonify({"erro": str(e)}), 400
```

```python
# models/produto.py — serialização centralizada em _row_to_dict
class ProdutoModel:

    @staticmethod
    def _row_to_dict(row) -> dict:          # uma única definição
        return {
            "id":        row["id"],
            "nome":      row["nome"],
            "descricao": row["descricao"],
            "preco":     row["preco"],
            "estoque":   row["estoque"],
            "categoria": row["categoria"],
            "ativo":     bool(row["ativo"]),
            "criado_em": row["criado_em"]
        }

    @staticmethod
    def get_todos() -> list[dict]:
        cursor.execute("SELECT * FROM produtos")
        return [ProdutoModel._row_to_dict(r) for r in cursor.fetchall()]  # reutiliza

    @staticmethod
    def buscar(...) -> list[dict]:
        ...
        return [ProdutoModel._row_to_dict(r) for r in cursor.fetchall()]  # reutiliza
```

### Passos de transformação

1. Identificar blocos idênticos ou >80% similares entre funções.
2. Extrair em função privada (`_parse_`, `_validar_`, `_row_to_dict`) no mesmo arquivo.
3. Para validação de body HTTP: extrair `_parse_<entidade>_body(dados)` na camada Routes.
4. Para serialização: extrair `_row_to_dict(row)` estático no Model.
5. Substituir todas as cópias pela chamada à função extraída.
6. Resolver AP-07 e AP-09 juntos quando duplicação envolve fetch de pedidos — `_agrupar_pedidos` serve aos dois.

### Checklist

- [ ] `_row_to_dict` existe em cada Model e é chamado em todos os SELECT
- [ ] `_parse_<entidade>_body` existe na Route e é chamado em POST e PUT
- [ ] Nenhum bloco de validação idêntico em 2+ funções

---

## PT-10 — Magic Numbers → Named Constants

**Anti-pattern:** AP-10 · **Severidade:** LOW
**Trigger:** literal numérico em fórmula de negócio; string de status repetida sem constante;
lista de valores válidos hardcoded inline.

### ANTES

```python
# models.py — magic numbers na lógica de desconto
if faturamento > 10000:
    desconto = faturamento * 0.1
elif faturamento > 5000:
    desconto = faturamento * 0.05
elif faturamento > 1000:
    desconto = faturamento * 0.02

# controllers.py — magic strings de status e categorias inline
categorias_validas = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]

if novo_status not in ["pendente", "aprovado", "enviado", "entregue", "cancelado"]:
    return jsonify({"erro": "Status inválido"}), 400
```

### DEPOIS

```python
# controllers/constants.py — constantes de domínio centralizadas
CATEGORIAS_PRODUTO = frozenset([
    "informatica", "moveis", "vestuario",
    "geral", "eletronicos", "livros"
])

STATUS_PEDIDO = frozenset([
    "pendente", "aprovado", "enviado", "entregue", "cancelado"
])

LIMITE_DESCONTO_ALTO   = 10_000
LIMITE_DESCONTO_MEDIO  = 5_000
LIMITE_DESCONTO_BAIXO  = 1_000
TAXA_DESCONTO_ALTO     = 0.10
TAXA_DESCONTO_MEDIO    = 0.05
TAXA_DESCONTO_BAIXO    = 0.02
```

```python
# controllers/relatorio_controller.py — usa constantes nomeadas
from controllers.constants import (
    LIMITE_DESCONTO_ALTO, LIMITE_DESCONTO_MEDIO, LIMITE_DESCONTO_BAIXO,
    TAXA_DESCONTO_ALTO, TAXA_DESCONTO_MEDIO, TAXA_DESCONTO_BAIXO
)

def _calcular_desconto(faturamento: float) -> float:
    if faturamento > LIMITE_DESCONTO_ALTO:
        return faturamento * TAXA_DESCONTO_ALTO
    if faturamento > LIMITE_DESCONTO_MEDIO:
        return faturamento * TAXA_DESCONTO_MEDIO
    if faturamento > LIMITE_DESCONTO_BAIXO:
        return faturamento * TAXA_DESCONTO_BAIXO
    return 0.0
```

### Passos de transformação

1. Criar `controllers/constants.py` (ou equivalente por domínio).
2. Extrair todo literal numérico de negócio para constante UPPER_CASE com nome explicativo.
3. Extrair listas de valores válidos para `frozenset` nomeado — imutável e com busca O(1).
4. Substituir todas as ocorrências inline pela referência à constante.
5. Importar as constantes onde necessário.

### Checklist

- [ ] Nenhum literal `0.1`, `0.05`, `0.02` em código de negócio sem constante nomeada
- [ ] Listas de status e categorias são `frozenset` importadas de `constants.py`
- [ ] Constantes em UPPER_SNAKE_CASE com nome que explica o significado de negócio

---

## PT-11 — Poor Naming → Semantic Rename

**Anti-pattern:** AP-11 · **Severidade:** LOW
**Trigger:** variáveis sequenciais (`cursor2`, `cursor3`); nomes genéricos (`data`, `result`,
`obj`); parâmetro `id` que sombreia built-in Python.

### ANTES

```python
# models.py — cursor2/cursor3 sequenciais sem significado
for row in rows:
    cursor2 = db.cursor()
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    itens = cursor2.fetchall()
    for item in itens:
        cursor3 = db.cursor()
        cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
        prod = cursor3.fetchone()

# controllers.py — parâmetro 'id' sombreia built-in Python
def buscar_produto(id):      # id() é built-in — risco de shadowing
    produto = models.get_produto_por_id(id)
```

### DEPOIS

```python
# models/pedido.py — cursores com nomes que revelam propósito
# (após PT-07, os cursores auxiliares desaparecem — substituídos por JOIN)
# Se cursores auxiliares ainda forem necessários em outros contextos:
cursor_pedidos  = db.cursor()
cursor_itens    = db.cursor()
cursor_produto  = db.cursor()
```

```python
# routes/produto_routes.py — parâmetro renomeado para evitar shadowing
@produto_bp.get("/<int:produto_id>")     # nome do path param descreve a entidade
def buscar_produto(produto_id: int):     # não mais 'id'
    try:
        produto = ProdutoController.buscar(produto_id)
        return jsonify({"dados": produto, "sucesso": True}), 200
    except LookupError:
        return jsonify({"erro": "Produto não encontrado"}), 404
```

```python
# models/produto.py — parâmetros com nomes semânticos
@staticmethod
def get_por_id(produto_id: int) -> dict | None:   # não mais 'id'
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))

@staticmethod
def atualizar(produto_id: int, nome: str, descricao: str,
              preco: float, estoque: int, categoria: str) -> None:
    cursor.execute(
        "UPDATE produtos SET nome=?, descricao=?, preco=?, estoque=?, categoria=? WHERE id=?",
        (nome, descricao, preco, estoque, categoria, produto_id)
    )
```

### Passos de transformação

1. Substituir todo parâmetro `id` por `<entidade>_id` (ex: `produto_id`, `usuario_id`, `pedido_id`).
2. Atualizar o path param no decorator Flask para usar o mesmo nome.
3. Após aplicar PT-07 (JOIN), `cursor2` e `cursor3` desaparecem naturalmente.
4. Se cursores auxiliares existirem em outros contextos, renomear descritivamente.
5. Renomear variáveis genéricas `result`, `data`, `rows` apenas quando o escopo for longo (>10 linhas).

### Checklist

- [ ] Zero parâmetros chamados `id` em funções Python (usa `produto_id`, `usuario_id`, etc.)
- [ ] Zero `cursor2`, `cursor3` no código final
- [ ] Path params nos decorators Flask coincidem com nomes dos parâmetros das funções

---

## Ordem de Aplicação Recomendada

Aplicar os padrões nesta sequência minimiza retrabalho — cada etapa cria a base para a próxima:

```
PT-06 (conexão por request)     → fundação para todos os Models
     ↓
PT-02 (env vars + senha hash)   → segurança antes de qualquer outra mudança
     ↓
PT-03 (SQL injection)           → corrige queries no código existente
     ↓
PT-01 (God File → Blueprints)   → cria a estrutura de diretórios alvo
     ↓
PT-05 (dependency injection)    → define interfaces entre camadas
     ↓
PT-04 (fat controller)          → separa negócio de HTTP
     ↓
PT-07 + PT-09 (N+1 + DRY)      → otimiza e deduplica juntos
     ↓
PT-08 (validação)               → adiciona validação na nova camada Routes
     ↓
PT-10 + PT-11 (constants + naming) → polimento final
```

## Validação Final

Após aplicar todos os padrões, executar o checklist de `architecture_guidelines.md` (Seção 9)
e confirmar que o servidor sobe e todos os endpoints respondem corretamente.
