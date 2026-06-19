================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~530 lines of code
Date:    2026-06-18

EXECUTIVE SUMMARY
-----------------
Total findings : 18
  CRITICAL     : 8
  HIGH         : 4
  MEDIUM       : 4
  LOW          : 2

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
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
---
Problem : O arquivo app.py centraliza inicialização do app, registro de rotas e handlers que
          executam SQL direto no banco. As funções reset_database e executar_query possuem
          cursor.execute misturado com decoradores @app.route, violando SRP e tornando
          impossível testar qualquer camada isoladamente.
Action  : Mover reset_database e executar_query para controllers (com autenticação adequada)
          e delegar o acesso ao banco para a camada models. app.py deve conter apenas
          inicialização do app e registro de rotas.

----------------------------------------------------------------

[CRITICAL] AP-02 — Hardcoded Credentials / Secrets in Source
File    : app.py
Lines   : 7–7
---
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
---
Problem : A chave secreta da aplicação está hardcoded no código-fonte e será exposta em
          qualquer commit ou repositório público. Qualquer pessoa com acesso ao código pode
          forjar sessões ou assinar tokens JWT usando essa chave.
Action  : Mover para variável de ambiente (os.environ.get("SECRET_KEY")) ou arquivo .env
          não versionado. Adicionar .env ao .gitignore e validar presença da variável na
          inicialização.

----------------------------------------------------------------

[CRITICAL] AP-02 — Hardcoded Credentials / Secrets in Source
File    : controllers.py
Lines   : 276–290
---
return jsonify({
    "status": "ok",
    "database": "connected",
    "counts": { ... },
    "versao": "1.0.0",
    "ambiente": "producao",
    "db_path": "loja.db",
    "debug": True,
    "secret_key": "minha-chave-super-secreta-123"
}), 200
---
Problem : O endpoint /health expõe a SECRET_KEY da aplicação, o caminho do banco de dados e
          a flag de debug na resposta HTTP sem qualquer autenticação. Qualquer cliente HTTP
          obtém as credenciais em claro.
Action  : Remover todos os campos de configuração interna da resposta pública do health
          check. Expor apenas status de conectividade. Proteger o endpoint com autenticação
          se necessário para observabilidade interna.

----------------------------------------------------------------

[CRITICAL] AP-02 — Hardcoded Credentials / Secrets in Source
File    : database.py
Lines   : 74–84
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
Problem : Senhas de usuários de seed estão em texto plano tanto no código-fonte quanto no
          banco de dados. A senha "admin123" do usuário admin representa risco crítico em
          qualquer ambiente. Além disso, armazenar senhas em texto plano viola LGPD e
          boas práticas de segurança.
Action  : Usar biblioteca de hashing (bcrypt, argon2-cffi) para armazenar hashes no banco.
          Mover dados de seed para arquivo de fixtures ou script separado não comitado com
          senhas reais.

----------------------------------------------------------------

[CRITICAL] AP-03 — SQL Injection (Concatenação Direta)
File    : models.py
Lines   : 108–119
---
def login_usuario(email, senha):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM usuarios WHERE email = '" + email +
        "' AND senha = '" + senha + "'"
    )
    row = cursor.fetchone()
---
Problem : A query de autenticação é construída por concatenação direta de email e senha
          vindos do usuário. Um atacante pode fazer bypass do login com email
          `' OR '1'='1` sem conhecer nenhuma senha, obtendo acesso como qualquer usuário.
Action  : Substituir concatenação por parâmetros parametrizados:
          cursor.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
          Adicionalmente, implementar hashing de senha e comparação via bcrypt.verify().

----------------------------------------------------------------

[CRITICAL] AP-03 — SQL Injection (Concatenação Direta)
File    : models.py
Lines   : 46–52
---
cursor.execute(
    "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES ('" +
    nome + "', '" + descricao + "', " + str(preco) + ", " +
    str(estoque) + ", '" + categoria + "')"
)
---
Problem : INSERT construído por concatenação de strings do usuário. Um atacante pode
          injetar SQL via campo nome ou descricao para alterar a estrutura da query,
          executar subqueries, ou manipular dados de outras tabelas.
Action  : Usar placeholders: cursor.execute("INSERT INTO produtos (nome, descricao, preco,
          estoque, categoria) VALUES (?,?,?,?,?)", (nome, descricao, preco, estoque, categoria))

----------------------------------------------------------------

[CRITICAL] AP-03 — SQL Injection (Concatenação Direta)
File    : models.py
Lines   : 285–299
---
def buscar_produtos(termo, categoria=None, preco_min=None, preco_max=None):
    query = "SELECT * FROM produtos WHERE 1=1"
    if termo:
        query += " AND (nome LIKE '%" + termo + "%' OR descricao LIKE '%" + termo + "%')"
    if categoria:
        query += " AND categoria = '" + categoria + "'"
    if preco_min:
        query += " AND preco >= " + str(preco_min)
    if preco_max:
        query += " AND preco <= " + str(preco_max)
    cursor.execute(query)
---
Problem : A query de busca constrói cláusulas LIKE e filtros por concatenação direta de
          parâmetros de query string. Um atacante pode usar termo=%' UNION SELECT... para
          exfiltrar dados de qualquer tabela do banco, incluindo senhas.
Action  : Usar placeholders para todos os parâmetros dinâmicos. Para LIKE, passar o
          padrão como argumento: cursor.execute("...nome LIKE ?", (f"%{termo}%",))

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
    try:
        cursor.execute(query)
        ...
---
Problem : O endpoint /admin/query executa qualquer SQL enviado pelo cliente sem qualquer
          autenticação, validação ou restrição. Permite leitura, escrita ou deleção total
          do banco. Em SQLite, pode ainda ser usado para ler arquivos do sistema via
          funções internas. É equivalente a expor um shell de banco de dados publicamente.
Action  : Remover completamente este endpoint. Se for necessário para operações de admin,
          implementar autenticação forte, lista branca de operações permitidas e auditoria
          de cada execução com log de quem executou o quê.

----------------------------------------------------------------

[HIGH] AP-04 — Fat Controller (Business Logic in Controller)
File    : controllers.py
Lines   : 24–62
---
def criar_produto():
    dados = request.get_json()
    if not dados: return jsonify(...), 400
    if "nome" not in dados: return jsonify(...), 400
    if "preco" not in dados: return jsonify(...), 400
    if "estoque" not in dados: return jsonify(...), 400
    nome = dados["nome"]; preco = dados["preco"]; estoque = dados["estoque"]
    if preco < 0: return jsonify(...), 400
    if len(nome) < 2: return jsonify(...), 400
    categorias_validas = ["informatica","moveis","vestuario","geral","eletronicos","livros"]
    if categoria not in categorias_validas: return jsonify(...), 400
---
Problem : O controller criar_produto contém 38 linhas de validações de domínio (regras de
          negócio como tamanho mínimo de nome, faixas de preço, lista de categorias válidas)
          que não pertencem à camada de apresentação. Impossível reutilizar ou testar essas
          regras sem simular uma requisição HTTP.
Action  : Extrair validações para uma camada de serviço (ProdutoService.validar) ou schema
          de validação (marshmallow/pydantic). O controller deve apenas fazer parse do body
          e delegar para o serviço.

----------------------------------------------------------------

[HIGH] AP-04 — Fat Controller (Business Logic in Controller)
File    : controllers.py
Lines   : 188–220
---
def criar_pedido():
    ...
    resultado = models.criar_pedido(usuario_id, itens)
    if "erro" in resultado:
        return jsonify(...), 400
    print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + " criado ...")
    print("ENVIANDO SMS: Seu pedido foi recebido!")
    print("ENVIANDO PUSH: Novo pedido recebido pelo sistema")
    return jsonify({...}), 201
---
Problem : O controller de criação de pedido orquestra side-effects de notificação (email,
          SMS, push) inline. Essas são responsabilidades de um serviço de notificação
          separado. O controller também decide quais notificações enviar baseado no resultado
          do modelo, o que é lógica de negócio.
Action  : Criar NotificacaoService com métodos enviar_email, enviar_sms, enviar_push.
          O controller chama PedidoService.criar(dados) que internamente dispara as
          notificações. Assim é possível testar e trocar o canal de notificação de forma
          independente.

----------------------------------------------------------------

[HIGH] AP-05 — Hard Coupling / No Dependency Injection
File    : models.py
Lines   : 1–10
---
from database import get_db
import sqlite3

def get_todos_produtos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos")
    ...

def criar_produto(nome, descricao, preco, estoque, categoria):
    db = get_db()
---
Problem : Todas as funções de models.py chamam get_db() diretamente via import acoplado à
          implementação concreta de database.py. Não há injeção de dependência nem abstração
          de repositório. Trocar de SQLite para PostgreSQL exige editar cada função; testar
          sem banco real é impossível sem monkey-patch frágil.
Action  : Introduzir uma classe Repository (ProdutoRepository, UsuarioRepository) que recebe
          a conexão como parâmetro no construtor. Injetar a conexão a partir do contexto da
          aplicação Flask (g ou factory pattern), permitindo passar uma conexão de teste nos
          unit tests.

----------------------------------------------------------------

[HIGH] AP-06 — Global Mutable State
File    : database.py
Lines   : 4–10
---
db_connection = None
db_path = "loja.db"

def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(db_path, check_same_thread=False)
---
Problem : db_connection é uma variável global mutável compartilhada por toda a aplicação.
          Em servidores multi-threaded (Gunicorn) isso causa race conditions onde múltiplas
          threads podem compartilhar a mesma conexão SQLite, resultando em erros ou dados
          corrompidos. check_same_thread=False mascara o problema sem resolvê-lo.
Action  : Usar Flask's g object (flask.g) para armazenar a conexão por request, com
          teardown_appcontext para fechá-la ao final. Cada request recebe uma conexão
          isolada, eliminando race conditions.

----------------------------------------------------------------

[MEDIUM] AP-07 — N+1 Query Problem
File    : models.py
Lines   : 171–201
---
cursor.execute("SELECT * FROM pedidos WHERE usuario_id = " + str(usuario_id))
rows = cursor.fetchall()
for row in rows:
    pedido = {...}
    cursor2 = db.cursor()
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    itens = cursor2.fetchall()
    for item in itens:
        cursor3 = db.cursor()
        cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
---
Problem : Para cada pedido é executada 1 query de itens, e para cada item mais 1 query de
          produto. Com N pedidos e M itens por pedido, o total é 1 + N + N*M queries. Com
          10 pedidos de 5 itens cada, são 61 queries onde 1 com JOIN bastaria.
Action  : Substituir por queries com JOIN:
          SELECT p.*, ip.*, pr.nome FROM pedidos p
          JOIN itens_pedido ip ON ip.pedido_id = p.id
          JOIN produtos pr ON pr.id = ip.produto_id
          WHERE p.usuario_id = ?

----------------------------------------------------------------

[MEDIUM] AP-07 — N+1 Query Problem
File    : models.py
Lines   : 203–232
---
cursor.execute("SELECT * FROM pedidos")
rows = cursor.fetchall()
for row in rows:
    pedido = {...}
    cursor2 = db.cursor()
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    itens = cursor2.fetchall()
    for item in itens:
        cursor3 = db.cursor()
        cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
---
Problem : Mesmo padrão N+1 de get_pedidos_usuario aplicado ao endpoint de listagem global
          de pedidos. Sem filtro de usuario_id, o impacto é ainda maior: com 100 pedidos de
          5 itens cada, são 601 queries por chamada ao endpoint /pedidos.
Action  : Mesmo que o finding anterior: consolidar em única query com JOIN. Considerar
          paginação obrigatória no endpoint para limitar volume de dados retornados.

----------------------------------------------------------------

[MEDIUM] AP-08 — Missing Input Validation at Route Level
File    : controllers.py
Lines   : 167–186
---
def login():
    try:
        dados = request.get_json()
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not email or not senha:
            return jsonify({"erro": "Email e senha são obrigatórios"}), 400
---
Problem : request.get_json() retorna None quando o Content-Type não é application/json ou
          o body é inválido. A chamada imediata a dados.get() lança AttributeError,
          resultando em resposta 500 que expõe stack trace ao cliente. Nenhuma biblioteca
          de validação de schema (marshmallow, pydantic) é usada no projeto.
Action  : Adicionar verificação de None antes de acessar campos: if not dados: return 400.
          Adotar marshmallow ou pydantic para validação declarativa de schemas, eliminando
          verificações manuais dispersas e padronizando mensagens de erro.

----------------------------------------------------------------

[MEDIUM] AP-09 — Code Duplication / Missing DRY
File    : models.py
Lines   : 171–232
---
# get_pedidos_usuario (171–201) e get_todos_pedidos (203–232)
# são quase idênticas: mesma estrutura de loop, mesmos cursors aninhados,
# mesma serialização do dict pedido e do dict item.
for row in rows:
    pedido = {"id": row["id"], "usuario_id": row["usuario_id"],
              "status": row["status"], "total": row["total"],
              "criado_em": row["criado_em"], "itens": []}
    cursor2 = db.cursor()
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = ...")
---
Problem : As funções get_pedidos_usuario e get_todos_pedidos diferem apenas no filtro WHERE.
          Todo o código de serialização de pedido e de busca de itens/produtos é duplicado.
          Qualquer mudança no formato de resposta exige edição em dois lugares com risco de
          divergência silenciosa.
Action  : Extrair função privada _serializar_pedidos(rows) que executa a lógica comum de
          busca de itens e serialização. As duas funções públicas apenas fazem a query
          inicial com filtro diferente e chamam a função compartilhada.

----------------------------------------------------------------

[LOW] AP-10 — Magic Numbers and Magic Strings
File    : models.py
Lines   : 255–262
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
---
Problem : Os limiares de faturamento (10000, 5000, 1000) e as taxas de desconto (0.1, 0.05,
          0.02) são números mágicos sem nome simbólico. É impossível saber se 0.1 é 10% de
          desconto ou outra coisa sem ler o contexto completo. Mudanças de política comercial
          exigem encontrar e editar cada literal.
Action  : Definir constantes nomeadas no topo do arquivo:
          DESCONTO_FATURAMENTO_ALTO = 0.10; LIMITE_FATURAMENTO_ALTO = 10_000
          Ou mover para uma tabela de configuração de descontos.

----------------------------------------------------------------

[LOW] AP-11 — Poor Naming / Semantic Misalignment
File    : controllers.py
Lines   : 56, 160
---
# linha 56
id = models.criar_produto(nome, descricao, preco, estoque, categoria)
print("Produto criado com ID: " + str(id))

# linha 160
id = models.criar_usuario(nome, email, senha)
---
Problem : A variável id sobrescreve a built-in id() do Python dentro do escopo das funções
          criar_produto e criar_usuario. Embora raramente impacte o comportamento, viola a
          convenção PEP8, confunde linters e torna o código mais difícil de inspecionar em
          debugging. O nome também é genérico demais para o domínio.
Action  : Renomear para produto_id e usuario_id respectivamente, alinhando com a nomenclatura
          do restante do projeto e evitando shadow da built-in.


================================================================
Findings : 18 total
================================================================
