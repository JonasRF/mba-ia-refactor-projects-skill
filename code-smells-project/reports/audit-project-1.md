================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~781 lines of code
Date:    2026-06-26

EXECUTIVE SUMMARY
-----------------
Total findings : 22
  CRITICAL     : 7
  HIGH         : 5
  MEDIUM       : 6
  LOW          : 4

================================================================
FINDINGS
================================================================

[CRITICAL] AP-01 — God Class / Monolith File
File    : app.py
Lines   : 47–78
---
@app.route("/admin/reset-db", methods=["POST"])
def reset_database():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM itens_pedido")
    cursor.execute("DELETE FROM pedidos")
    cursor.execute("DELETE FROM produtos")
    cursor.execute("DELETE FROM usuarios")
    db.commit()
---
Problem : app.py concentra inicialização da aplicação, registro de rotas E handlers inline com acesso direto ao banco. As rotas /admin/reset-db e /admin/query executam lógica de persistência sem passar pelas camadas Model/Controller, violando completamente a separação de responsabilidades.
Action  : Mover rotas admin para routes/admin.py; delegar acesso ao banco ao model layer; app.py deve conter apenas bootstrap e registro de blueprints.

----------------------------------------------------------------

[CRITICAL] AP-02 — Hardcoded Credentials / Secrets in Source
File    : app.py
Lines   : 7–8
---
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
---
Problem : A SECRET_KEY é um literal hardcoded diretamente no código-fonte. Qualquer commit expõe a chave no histórico git; repositórios públicos ou leaks de código comprometem toda a segurança de sessão.
Action  : Substituir por variável de ambiente: `app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")`. Nunca comitar secrets reais.

----------------------------------------------------------------

[CRITICAL] AP-02 — Hardcoded Credentials / Secrets in Source
File    : database.py
Lines   : 73–83
---
usuarios = [
    ("Admin", "admin@loja.com", "admin123", "admin"),
    ("João Silva", "joao@email.com", "123456", "cliente"),
    ("Maria Santos", "maria@email.com", "senha123", "cliente"),
]
cursor.executemany(
    "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
    usuarios
)
---
Problem : Credenciais de usuários default com senhas em plaintext estão hardcoded na inicialização do banco. As senhas não são hasheadas e ficam expostas em qualquer acesso ao código-fonte ou ao arquivo .db.
Action  : Remover seed data do código-fonte; usar script de seed separado (fora do versionamento) com senhas hasheadas via bcrypt/argon2. Nunca armazenar senhas em texto claro.

----------------------------------------------------------------

[CRITICAL] AP-02 — Hardcoded Credentials / Secrets in Source
File    : controllers.py
Lines   : 285–290
---
return jsonify({
    "status": "ok",
    "database": "connected",
    "versao": "1.0.0",
    "ambiente": "producao",
    "db_path": "loja.db",
    "debug": True,
    "secret_key": "minha-chave-super-secreta-123"
}), 200
---
Problem : A SECRET_KEY é explicitamente retornada no response do endpoint /health. Qualquer cliente HTTP (incluindo usuários não autenticados) pode obter a chave de assinatura de sessão, comprometendo completamente a segurança.
Action  : Remover secret_key, debug, db_path do response. Health check deve retornar apenas status operacional (status, database, versao, counts).

----------------------------------------------------------------

[CRITICAL] AP-03 — SQL Injection (Concatenação Direta)
File    : app.py
Lines   : 59–78
---
@app.route("/admin/query", methods=["POST"])
def executar_query():
    dados = request.get_json()
    query = dados.get("sql", "")
    if not query:
        return jsonify({"erro": "Query não informada"}), 400
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query)
---
Problem : Endpoint aceita SQL arbitrário do usuário e o executa diretamente sem autenticação, sanitização ou restrição. É um backdoor completo: qualquer cliente pode executar DROP TABLE, SELECT de dados sensíveis, ou criar usuários admin.
Action  : Remover este endpoint imediatamente. Se administração de banco for necessária, usar ferramentas CLI autenticadas (ex: sqlite3 CLI restrito ao servidor).

----------------------------------------------------------------

[CRITICAL] AP-03 — SQL Injection (Concatenação Direta)
File    : models.py
Lines   : 105–111
---
cursor.execute(
    "SELECT * FROM usuarios WHERE email = '" + email +
    "' AND senha = '" + senha + "'"
)
---
Problem : A query de login é construída por concatenação de strings. Um atacante pode usar `' OR '1'='1` no campo email para bypass completo de autenticação, obtendo acesso como qualquer usuário.
Action  : Usar query parametrizada: `cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha_hash))`. Também implementar hashing de senha.

----------------------------------------------------------------

[CRITICAL] AP-03 — SQL Injection (Concatenação Direta)
File    : models.py
Lines   : 47–50
---
cursor.execute(
    "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES ('" +
    nome + "', '" + descricao + "', " + str(preco) + ", " + str(estoque) + ", '" + categoria + "')"
)
---
Problem : Query INSERT construída por concatenação de nome e descricao permite injeção SQL via campos de texto. Um nome como `'); DROP TABLE produtos; --` destruiria a tabela.
Action  : Usar placeholders: `cursor.execute("INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)", (nome, descricao, preco, estoque, categoria))`.

----------------------------------------------------------------

[HIGH] AP-04 — Fat Controller (Business Logic in Controller)
File    : models.py
Lines   : 133–169
---
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
---
Problem : Validação de estoque, cálculo de total e orquestração de múltiplas entidades (produtos, pedidos, itens_pedido) vivem na camada Model. Models devem apenas persistir dados; regras de negócio pertencem a uma camada Service.
Action  : Extrair para `PedidoService.criar_pedido(usuario_id, itens)`. O model deve expor apenas `PedidoModel.inserir(usuario_id, total)` e `ItemPedidoModel.inserir(pedido_id, produto_id, quantidade, preco)`.

----------------------------------------------------------------

[HIGH] AP-04 — Fat Controller (Business Logic in Controller)
File    : models.py
Lines   : 235–273
---
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
---
Problem : Regras de negócio para cálculo de desconto progressivo (tiers de faturamento) estão implementadas na camada Model. Esta lógica é domain business logic e deve residir em uma Service ou camada de domínio.
Action  : Extrair para `RelatorioService.calcular_desconto(faturamento) -> float`. O model deve apenas retornar os dados agregados brutos do banco.

----------------------------------------------------------------

[HIGH] AP-04 — Fat Controller (Business Logic in Controller)
File    : controllers.py
Lines   : 188–220
---
resultado = models.criar_pedido(usuario_id, itens)
if "erro" in resultado:
    return jsonify({"erro": resultado["erro"], "sucesso": False}), 400
print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + " criado para usuario " + str(usuario_id))
print("ENVIANDO SMS: Seu pedido foi recebido!")
print("ENVIANDO PUSH: Novo pedido recebido pelo sistema")
---
Problem : Lógica de side-effects (email, SMS, push notification) está hardcoded no controller. O controller viola SRP ao assumir responsabilidade de notificação além de coordenar request/response.
Action  : Extrair para `NotificacaoService.notificar_pedido_criado(pedido_id, usuario_id)`. Injetar o serviço no controller.

----------------------------------------------------------------

[HIGH] AP-05 — Hard Coupling / No Dependency Injection
File    : models.py
Lines   : 1–6
---
from database import get_db
import sqlite3

def get_todos_produtos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos")
---
Problem : Todas as funções de model importam e chamam `get_db()` diretamente — acoplamento rígido ao singleton global de conexão. Impossível injetar conexão de teste ou mock do banco, tornando testes unitários inviáveis.
Action  : Usar Flask `g` para conexão escopada por request; ou aceitar `db` como parâmetro nas funções de model para possibilitar injeção em testes.

----------------------------------------------------------------

[HIGH] AP-06 — Global Mutable State
File    : database.py
Lines   : 4–11
---
db_connection = None
db_path = "loja.db"

def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(db_path, check_same_thread=False)
        db_connection.row_factory = sqlite3.Row
---
Problem : `db_connection` é uma variável global mutável compartilhada entre todas as requisições. O `check_same_thread=False` suprime a proteção nativa do sqlite3, expondo race conditions em servidor multi-thread. Uma conexão única para toda a aplicação também não libera recursos entre requests.
Action  : Escopar conexão por request via Flask `g`: `g.db = sqlite3.connect(...)` com teardown `@app.teardown_appcontext def close_db(e): g.pop("db", None).close()`.

----------------------------------------------------------------

[MEDIUM] AP-07 — N+1 Query Problem
File    : models.py
Lines   : 186–199
---
cursor2 = db.cursor()
cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
itens = cursor2.fetchall()
for item in itens:
    cursor3 = db.cursor()
    cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
    prod = cursor3.fetchone()
---
Problem : Para cada pedido, uma query busca seus itens; para cada item, outra query busca o nome do produto. 10 pedidos com 5 itens cada = 61 queries (1 + 10 + 50). Performance degrada linearmente com volume.
Action  : Substituir por JOIN único: `SELECT p.*, i.*, pr.nome FROM pedidos p JOIN itens_pedido i ON i.pedido_id = p.id JOIN produtos pr ON pr.id = i.produto_id WHERE p.usuario_id = ?`.

----------------------------------------------------------------

[MEDIUM] AP-07 — N+1 Query Problem
File    : models.py
Lines   : 218–232
---
cursor2 = db.cursor()
cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
itens = cursor2.fetchall()
for item in itens:
    cursor3 = db.cursor()
    cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
    prod = cursor3.fetchone()
---
Problem : `get_todos_pedidos` replica o mesmo padrão N+1 de `get_pedidos_usuario`. Para toda a base de pedidos este padrão é catastrófico em produção — 1000 pedidos = milhares de queries por request.
Action  : Usar JOIN abrangendo pedidos, itens_pedido e produtos. Extrair lógica de serialização para helper `_build_pedidos_com_itens(rows)` reutilizável pelas duas funções.

----------------------------------------------------------------

[MEDIUM] AP-08 — Missing Input Validation at Route Level
File    : controllers.py
Lines   : 118–121
---
if preco_min:
    preco_min = float(preco_min)
if preco_max:
    preco_max = float(preco_max)
---
Problem : `float()` em query string sem try/except lança `ValueError` se o cliente enviar um valor não-numérico (ex: `?preco_min=abc`), resultando em HTTP 500 com stack trace exposto.
Action  : Envolver em try/except: `try: preco_min = float(preco_min) except ValueError: return jsonify({"erro": "preco_min deve ser numérico"}), 400`.

----------------------------------------------------------------

[MEDIUM] AP-08 — Missing Input Validation at Route Level
File    : controllers.py
Lines   : 237–241
---
def atualizar_status_pedido(pedido_id):
    try:
        dados = request.get_json()
        novo_status = dados.get("status", "")
---
Problem : Se o request body for ausente, mal-formado ou Content-Type inválido, `request.get_json()` retorna `None` e `None.get(...)` lança `AttributeError` — HTTP 500 não tratado.
Action  : Adicionar guarda: `if not dados: return jsonify({"erro": "Body JSON obrigatório"}), 400` antes de acessar campos do dict.

----------------------------------------------------------------

[MEDIUM] AP-09 — Code Duplication / Missing DRY
File    : models.py
Lines   : 12–21, 30–40, 303–313
---
result.append({
    "id": row["id"],
    "nome": row["nome"],
    "descricao": row["descricao"],
    "preco": row["preco"],
    "estoque": row["estoque"],
    "categoria": row["categoria"],
    "ativo": row["ativo"],
    "criado_em": row["criado_em"]
})
---
Problem : O dict de serialização de produto é copiado identicamente em `get_todos_produtos`, `get_produto_por_id` e `buscar_produtos`. Qualquer campo novo ou renomeado exige alteração em 3 locais.
Action  : Extrair para `def _serialize_produto(row) -> dict` e chamar nas três funções.

----------------------------------------------------------------

[MEDIUM] AP-09 — Code Duplication / Missing DRY
File    : models.py
Lines   : 171–233
---
def get_pedidos_usuario(usuario_id):
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ...")
    # ~30 linhas de lógica de serialização com cursors aninhados

def get_todos_pedidos():
    cursor.execute("SELECT * FROM pedidos")
    # ~30 linhas idênticas de lógica de serialização com cursors aninhados
---
Problem : `get_pedidos_usuario` e `get_todos_pedidos` diferem apenas na cláusula WHERE mas compartilham ~30 linhas de lógica idêntica de serialização com cursors aninhados. Qualquer correção (ex: bug no N+1) deve ser aplicada em dois lugares.
Action  : Extrair `_serialize_pedidos_com_itens(rows, db) -> list` e invocar de ambas as funções com apenas a query inicial diferente.

----------------------------------------------------------------

[LOW] AP-10 — Magic Numbers and Magic Strings
File    : models.py
Lines   : 256–259
---
if faturamento > 10000:
    desconto = faturamento * 0.1
elif faturamento > 5000:
    desconto = faturamento * 0.05
elif faturamento > 1000:
    desconto = faturamento * 0.02
---
Problem : Os limiares de desconto (10000, 5000, 1000) e os multiplicadores (0.1, 0.05, 0.02) são magic numbers sem nome simbólico. Intenção e regra de negócio ficam obscurecidas; mudança de política exige caça manual no código.
Action  : Definir constantes nomeadas: `LIMITE_DESCONTO_ALTO = 10_000; TAXA_DESCONTO_ALTO = 0.10; ...` preferencialmente em config.py.

----------------------------------------------------------------

[LOW] AP-10 — Magic Numbers and Magic Strings
File    : controllers.py
Lines   : 52–54, 242
---
categorias_validas = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
...
if novo_status not in ["pendente", "aprovado", "enviado", "entregue", "cancelado"]:
---
Problem : Listas de categorias válidas e status válidos são magic strings inline em funções. Os mesmos valores provavelmente são necessários em validações, relatórios e testes mas não há fonte única de verdade.
Action  : Definir como constantes de módulo ou enum: `CATEGORIAS_VALIDAS = frozenset({...}); STATUS_PEDIDO = frozenset({...})` em um arquivo `constants.py`.

----------------------------------------------------------------

[LOW] AP-11 — Poor Naming / Semantic Misalignment
File    : models.py
Lines   : 187, 219, 222, 225
---
cursor2 = db.cursor()
cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
itens = cursor2.fetchall()
for item in itens:
    cursor3 = db.cursor()
    cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
---
Problem : `cursor2` e `cursor3` são nomes sequenciais sem semântica. Ao ler o código não é possível identificar rapidamente qual cursor consulta itens e qual consulta produtos.
Action  : Renomear para `itens_cursor` e `produto_cursor` respectivamente para comunicar intenção.

----------------------------------------------------------------

[LOW] AP-11 — Poor Naming / Semantic Misalignment
File    : controllers.py
Lines   : 56, 160
---
id = models.criar_produto(nome, descricao, preco, estoque, categoria)
...
id = models.criar_usuario(nome, email, senha)
---
Problem : `id` como nome de variável local sobrescreve a built-in `id()` do Python. Além de má prática, o nome é ambíguo quando múltiplas entidades são criadas no mesmo escopo.
Action  : Renomear para `produto_id` e `usuario_id` respectivamente — mais descritivo e sem shadowing de built-in.


================================================================
Findings : 22
================================================================
