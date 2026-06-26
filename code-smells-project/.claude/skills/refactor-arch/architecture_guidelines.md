# Architecture Guidelines — MVC Target Pattern

Este arquivo define a arquitetura-alvo que a skill `refactor-arch` deve produzir na **Fase 3
(Refatoração)**. É a única fonte de verdade sobre como cada camada deve ser estruturada,
quais responsabilidades pertencem a cada camada e como as camadas se comunicam.

As regras são agnósticas de linguagem. Exemplos são fornecidos em Python/Flask (stack de referência),
mas os princípios aplicam-se a qualquer stack detectada na Fase 1.

---

## 1. Estrutura de Diretórios Alvo

```
<raiz do projeto>/
├── app.py                  # Bootstrap: cria a app, registra Blueprints, lê env vars
├── config.py               # Configurações por ambiente (Development, Production, Testing)
├── .env.example            # Template de variáveis de ambiente (sem valores reais)
├── requirements.txt
│
├── models/                 # Camada Model — entidades e acesso a dados
│   ├── __init__.py
│   ├── produto.py
│   ├── usuario.py
│   └── pedido.py
│
├── controllers/            # Camada Controller — lógica de negócio e orquestração
│   ├── __init__.py
│   ├── produto_controller.py
│   ├── usuario_controller.py
│   └── pedido_controller.py
│
├── routes/                 # Camada View/Routes — parsing de HTTP e serialização
│   ├── __init__.py
│   ├── produto_routes.py
│   ├── usuario_routes.py
│   └── pedido_routes.py
│
├── services/               # (opcional) Serviços de infraestrutura: email, SMS, fila
│   ├── __init__.py
│   └── notification_service.py
│
├── database/               # Gerenciamento de conexão e schema
│   ├── __init__.py
│   └── connection.py
│
└── reports/                # Relatórios de auditoria (não é camada da aplicação)
```

> **Regra de nomenclatura:** diretórios em minúsculas, arquivos em snake_case, classes em PascalCase.
> Cada entidade de domínio tem um arquivo próprio em cada camada — não concentrar múltiplas entidades
> no mesmo arquivo.

---

## 2. Camada Model

### 2.1 Responsabilidade

A camada Model é responsável exclusivamente por:

- Representar a estrutura de uma entidade de domínio (atributos e tipos).
- Encapsular o acesso ao banco de dados para aquela entidade (queries parametrizadas).
- Retornar dados como dicionários Python ou objetos simples — sem lógica de negócio.

### 2.2 Regras obrigatórias

| # | Regra |
|---|-------|
| M-01 | Toda query SQL deve usar placeholders parametrizados (`?` para SQLite, `%s` para PostgreSQL). **Nunca concatenar** variáveis em strings SQL. |
| M-02 | O Model não importa nada de `flask`, `request` ou qualquer camada de Controller/Routes. |
| M-03 | Senhas devem ser hasheadas antes de persistir (bcrypt/argon2). O Model nunca armazena ou retorna senha em texto plano. |
| M-04 | A serialização de cada entidade deve ser feita por um método `to_dict()` centralizado no próprio Model — não replicar em múltiplos lugares. |
| M-05 | O Model não toma decisões de negócio (ex: calcular desconto, verificar estoque suficiente). Ele expõe dados; quem decide é o Controller. |
| M-06 | Queries que envolvem múltiplas tabelas relacionadas devem usar JOIN em vez de múltiplas queries em loop (evitar N+1). |

### 2.3 Estrutura padrão de um arquivo Model

```python
# models/produto.py
from database.connection import get_db

class ProdutoModel:

    @staticmethod
    def get_todos() -> list[dict]:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM produtos WHERE ativo = 1")
        return [ProdutoModel._row_to_dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_por_id(produto_id: int) -> dict | None:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        row = cursor.fetchone()
        return ProdutoModel._row_to_dict(row) if row else None

    @staticmethod
    def criar(nome: str, descricao: str, preco: float, estoque: int, categoria: str) -> int:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def _row_to_dict(row) -> dict:
        return {
            "id": row["id"],
            "nome": row["nome"],
            "descricao": row["descricao"],
            "preco": row["preco"],
            "estoque": row["estoque"],
            "categoria": row["categoria"],
            "ativo": bool(row["ativo"]),
            "criado_em": row["criado_em"]
        }
```

---

## 3. Camada Controller

### 3.1 Responsabilidade

A camada Controller é responsável exclusivamente por:

- Receber dados já validados e parseados (vindos da camada Routes).
- Executar regras de negócio: calcular, decidir, orquestrar chamadas a Models.
- Coordenar serviços de infraestrutura (notificação, fila) via injeção de dependência.
- Retornar resultado da operação como dicionário Python — sem conhecer HTTP.

### 3.2 Regras obrigatórias

| # | Regra |
|---|-------|
| C-01 | O Controller não importa `request`, `jsonify` ou qualquer objeto HTTP. Entrada e saída são tipos Python puros. |
| C-02 | O Controller não acessa o banco diretamente — toda persistência passa pelo Model. |
| C-03 | Regras de validação de domínio (limites, categorias válidas, invariantes) vivem no Controller — não na camada Routes. |
| C-04 | Notificações externas (email, SMS, push) são delegadas a um serviço injetado como parâmetro — não implementadas inline. |
| C-05 | Em caso de erro de negócio, o Controller levanta exceções tipadas (ex: `ValueError`, `PermissionError`) — não retorna dicts com chave `"erro"`. |
| C-06 | O Controller não formata a resposta final (não converte para JSON, não define status HTTP). |

### 3.3 Estrutura padrão de um arquivo Controller

```python
# controllers/produto_controller.py
from models.produto import ProdutoModel

CATEGORIAS_VALIDAS = frozenset(["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"])

class ProdutoController:

    @staticmethod
    def listar() -> list[dict]:
        return ProdutoModel.get_todos()

    @staticmethod
    def criar(nome: str, descricao: str, preco: float, estoque: int, categoria: str) -> dict:
        if len(nome) < 2 or len(nome) > 200:
            raise ValueError("Nome deve ter entre 2 e 200 caracteres")
        if preco < 0:
            raise ValueError("Preço não pode ser negativo")
        if estoque < 0:
            raise ValueError("Estoque não pode ser negativo")
        if categoria not in CATEGORIAS_VALIDAS:
            raise ValueError(f"Categoria inválida. Válidas: {sorted(CATEGORIAS_VALIDAS)}")

        produto_id = ProdutoModel.criar(nome, descricao, preco, estoque, categoria)
        return {"id": produto_id}

    @staticmethod
    def buscar(produto_id: int) -> dict:
        produto = ProdutoModel.get_por_id(produto_id)
        if not produto:
            raise LookupError("Produto não encontrado")
        return produto
```

---

## 4. Camada Routes (View)

### 4.1 Responsabilidade

A camada Routes é responsável exclusivamente por:

- Definir as rotas HTTP e os métodos aceitos (GET, POST, PUT, DELETE).
- Fazer o parsing do request: extrair e converter parâmetros de path, query string e body JSON.
- Validar a **presença e o tipo** dos campos obrigatórios antes de chamar o Controller.
- Chamar o Controller com tipos Python puros.
- Capturar exceções do Controller e mapeá-las para status HTTP correto.
- Serializar a resposta do Controller para JSON.

### 4.2 Regras obrigatórias

| # | Regra |
|---|-------|
| R-01 | Cada arquivo de routes define um `Blueprint` Flask — não registrar rotas diretamente no objeto `app`. |
| R-02 | A camada Routes não contém lógica de negócio. Validação se limita à presença e tipo dos campos do request. |
| R-03 | Capturar exceções do Controller e mapear para status HTTP: `ValueError` → 400, `LookupError` → 404, `PermissionError` → 403, `Exception` → 500. |
| R-04 | Nunca retornar stack traces ou mensagens internas ao cliente em respostas de erro de produção. |
| R-05 | Toda credencial, chave secreta e configuração sensível deve vir de variáveis de ambiente — nunca hardcoded na camada Routes ou em qualquer outra. |
| R-06 | A camada Routes não acessa o banco diretamente. |

### 4.3 Estrutura padrão de um arquivo Routes

```python
# routes/produto_routes.py
from flask import Blueprint, request, jsonify
from controllers.produto_controller import ProdutoController

produto_bp = Blueprint("produtos", __name__, url_prefix="/produtos")

@produto_bp.get("/")
def listar_produtos():
    produtos = ProdutoController.listar()
    return jsonify({"dados": produtos, "sucesso": True}), 200

@produto_bp.post("/")
def criar_produto():
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Body JSON inválido ou ausente"}), 400

    campos_obrigatorios = ["nome", "preco", "estoque"]
    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({"erro": f"Campo obrigatório ausente: {campo}"}), 400

    try:
        resultado = ProdutoController.criar(
            nome=dados["nome"],
            descricao=dados.get("descricao", ""),
            preco=float(dados["preco"]),
            estoque=int(dados["estoque"]),
            categoria=dados.get("categoria", "geral")
        )
        return jsonify({"dados": resultado, "sucesso": True}), 201
    except (TypeError, ValueError) as e:
        return jsonify({"erro": str(e)}), 400

@produto_bp.get("/<int:produto_id>")
def buscar_produto(produto_id):
    try:
        produto = ProdutoController.buscar(produto_id)
        return jsonify({"dados": produto, "sucesso": True}), 200
    except LookupError as e:
        return jsonify({"erro": str(e)}), 404
```

---

## 5. Camada Database (Infraestrutura)

### 5.1 Responsabilidade

- Gerenciar o ciclo de vida da conexão com o banco de dados.
- Fornecer uma conexão por request (usando `flask.g`).
- Criar o schema (tabelas) na inicialização se não existirem.
- Não conter lógica de negócio, queries de domínio ou seed de dados de produção.

### 5.2 Regras obrigatórias

| # | Regra |
|---|-------|
| D-01 | Usar `flask.g` para escopar a conexão por request — não usar variável global mutável. |
| D-02 | Registrar `teardown_appcontext` para fechar a conexão ao fim de cada request. |
| D-03 | O path do banco e demais configurações vêm de `app.config` (que lê de variáveis de ambiente). |
| D-04 | Seed de dados de desenvolvimento deve ser separado do código de schema e nunca executado em produção. |

### 5.3 Estrutura padrão

```python
# database/connection.py
import sqlite3
import flask

def get_db():
    if "db" not in flask.g:
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
    app.teardown_appcontext(close_db)
```

---

## 6. Bootstrap (app.py)

`app.py` deve ser mínimo. Responsabilidades:

- Ler variáveis de ambiente e instanciar o objeto `Flask`.
- Registrar todos os Blueprints.
- Registrar extensões (CORS, etc.).
- **Não conter rotas, lógica de negócio ou acesso a banco.**

```python
# app.py
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
    app.config["DATABASE"] = os.environ.get("DATABASE_PATH", "loja.db")
    app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    if config:
        app.config.update(config)

    CORS(app)
    init_app(app)

    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(pedido_bp)

    return app

if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000)
```

---

## 7. Fluxo de uma Requisição (Diagrama)

```
HTTP Request
     │
     ▼
┌──────────────┐
│    Routes    │  Parse request, valida presença/tipo de campos,
│  (Blueprint) │  chama Controller, captura exceções → status HTTP
└──────┬───────┘
       │ tipos Python puros
       ▼
┌──────────────┐
│  Controller  │  Regras de negócio, validação de domínio,
│              │  orquestra Models e Services
└──────┬───────┘
       │
       ├──────────────────────────┐
       ▼                          ▼
┌──────────────┐         ┌────────────────┐
│    Model     │         │    Service     │
│              │         │ (notification, │
│  SQL queries │         │  email, fila)  │
│  tipadas e   │         └────────────────┘
│  seguras     │
└──────┬───────┘
       │
       ▼
   Database
```

---

## 8. Mapeamento de Anti-Patterns → Camada Correta

Esta tabela relaciona cada anti-pattern do catálogo com a camada que o resolve:

| Anti-Pattern | Camada responsável pela correção |
|--------------|----------------------------------|
| AP-01 God Class | Decompor em Routes + Controller + Model + Database separados |
| AP-02 Hardcoded Secrets | `app.py` + `config.py` lendo `os.environ` |
| AP-03 SQL Injection | Model — substituir concatenação por placeholders parametrizados |
| AP-04 Fat Controller | Mover regras de domínio para Controller; side-effects para Service |
| AP-05 Hard Coupling | Injetar dependências; criar abstrações em `services/` |
| AP-06 Global Mutable State | Database — usar `flask.g` com escopo por request |
| AP-07 N+1 Query | Model — substituir loops de queries por JOIN |
| AP-08 Missing Validation | Routes — validar presença/tipo; Controller — validar domínio |
| AP-09 Code Duplication | Model — `to_dict()` centralizado; Controller — validadores reutilizáveis |
| AP-10 Magic Numbers | Controller — constantes nomeadas no topo do arquivo |
| AP-11 Poor Naming | Todos os arquivos — nomes semânticos alinhados ao domínio |

---

## 9. Checklist de Validação Pós-Refatoração

Antes de declarar a Fase 3 concluída, verificar:

- [ ] Nenhum arquivo em `routes/` contém strings SQL ou imports de `database/`.
- [ ] Nenhum arquivo em `controllers/` importa `request` ou `jsonify`.
- [ ] Nenhum arquivo em `models/` importa `flask` ou `controllers/`.
- [ ] Todas as queries SQL usam placeholders (`?` ou `%s`) — zero concatenação de string.
- [ ] `SECRET_KEY` e demais credenciais lidas de `os.environ` — ausentes do código-fonte.
- [ ] Senhas armazenadas com hash (bcrypt/argon2) — nunca em texto plano.
- [ ] `app.py` não contém rotas ou lógica de negócio — apenas bootstrap.
- [ ] `flask.g` usado para conexão de banco — sem variável global `db_connection`.
- [ ] Funções N+1 substituídas por JOIN — sem queries dentro de loops.
- [ ] Servidor sobe (`python app.py`) e todos os endpoints respondem corretamente.
- [ ] Endpoints testados manualmente: criar, listar, buscar por ID, atualizar, deletar, login, pedido.
