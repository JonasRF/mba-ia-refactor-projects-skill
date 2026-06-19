================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code
Date:    2026-06-18

EXECUTIVE SUMMARY
-----------------
Total findings : 11
  CRITICAL     : 3
  HIGH         : 3
  MEDIUM       : 3
  LOW          : 2

================================================================
FINDINGS
================================================================

[CRITICAL] AP-02 — Hardcoded Credentials / Secrets in Source
File    : app.py
Lines   : 7–7
---
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
---
Problem : A SECRET_KEY está hardcoded no código-fonte e é reexposta literalmente na resposta
          JSON do endpoint /health (controllers.py:289). Qualquer pessoa com acesso ao repositório
          ou ao endpoint de health check obtém a chave de sessão da aplicação, permitindo forjar
          cookies/tokens de sessão autenticados.
Action  : Mover SECRET_KEY para variável de ambiente (os.environ.get("SECRET_KEY")) e remover
          completamente o campo "secret_key" da resposta do health_check.

----------------------------------------------------------------

[CRITICAL] AP-03 — SQL Injection (Concatenação Direta) — Login Auth Bypass
File    : models.py
Lines   : 109–111
---
cursor.execute(
    "SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"
)
---
Problem : A query de autenticação é construída por concatenação de strings com dados do usuário.
          Um atacante pode autenticar-se como qualquer usuário sem senha usando o payload clássico:
          email = "admin@loja.com' --" (comenta o restante da query). Permite bypass total de
          autenticação e acesso irrestrito à conta admin.
Action  : Substituir todas as concatenações por placeholders parametrizados:
          cursor.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, senha))
          Aplicar o mesmo padrão em TODOS os cursor.execute do models.py (28 ocorrências).

----------------------------------------------------------------

[CRITICAL] AP-03 — SQL Injection — Endpoint de Execução Arbitrária de SQL
File    : app.py
Lines   : 59–78
---
@app.route("/admin/query", methods=["POST"])
def executar_query():
    dados = request.get_json()
    query = dados.get("sql", "")
    ...
    cursor.execute(query)
---
Problem : O endpoint /admin/query aceita qualquer string SQL via body e a executa diretamente
          no banco, sem autenticação, sem whitelist de operações e sem sanitização. Isso equivale
          a um backdoor de acesso total ao banco de dados para qualquer cliente HTTP, permitindo
          exfiltração, deleção ou corrupção completa dos dados.
Action  : Remover este endpoint completamente. Se uma interface de admin for necessária, ela deve
          exigir autenticação forte, usar queries parametrizadas e estar protegida por firewall/VPN.

----------------------------------------------------------------

[HIGH] AP-01 — God Class / Monolith File — Admin Routes com SQL Direto
File    : app.py
Lines   : 47–57
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
Problem : O arquivo de entrada da aplicação (app.py) mistura definição de rotas com acesso direto
          ao banco de dados e lógica destrutiva, violando o SRP. Operações de banco deveriam estar
          na camada de models/repository, e operações administrativas deveriam exigir autenticação.
          O endpoint /admin/reset-db apaga todos os dados sem qualquer proteção de acesso.
Action  : Extrair operações de banco para métodos no models.py. Proteger rotas /admin com
          middleware de autenticação. O arquivo app.py deve conter apenas inicialização e
          registro de rotas.

----------------------------------------------------------------

[HIGH] AP-04 — Fat Controller (Business Logic in Controller)
File    : controllers.py
Lines   : 188–220
---
def criar_pedido():
    ...
    resultado = models.criar_pedido(usuario_id, itens)
    ...
    print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + "...")
    print("ENVIANDO SMS: Seu pedido foi recebido!")
    print("ENVIANDO PUSH: Novo pedido recebido pelo sistema")
---
Problem : O controller de pedidos executa validação de entrada, orquestra a criação, dispara
          notificações (email, SMS, push) e gerencia erros — tudo na mesma função. Lógica de
          notificação e regras de negócio (validação de categorias em criar_produto, cálculo de
          desconto em relatorio_vendas) pertencem a uma camada de serviço, não ao controller.
          Impossível testar notificações sem disparar uma request HTTP completa.
Action  : Criar camada services/ com ProdutoService, PedidoService e NotificacaoService.
          Controllers devem apenas: (1) extrair dados da request, (2) chamar o serviço,
          (3) retornar a response HTTP.

----------------------------------------------------------------

[HIGH] AP-05/AP-06 — Hard Coupling + Global Mutable State (Singleton de Conexão)
File    : database.py
Lines   : 4–11
---
db_connection = None
db_path = "loja.db"

def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(db_path, check_same_thread=False)
---
Problem : A conexão com o banco é um singleton global mutável compartilhado entre todos os módulos
          (models.py e controllers.py importam get_db diretamente). Em servidores multi-threaded
          isso causa race conditions. Impossível injetar uma conexão de teste sem monkey-patching
          do módulo. O flag check_same_thread=False mascara o problema em vez de resolvê-lo.
Action  : Usar o padrão de context de aplicação do Flask (flask.g) para conexões por-request, ou
          adotar um pool de conexões. Passar a conexão como parâmetro (dependency injection) em vez
          de importar o singleton diretamente nos módulos de modelo.

----------------------------------------------------------------

[MEDIUM] AP-07 — N+1 Query Problem
File    : models.py
Lines   : 171–201
---
cursor.execute("SELECT * FROM pedidos WHERE usuario_id = " + str(usuario_id))
rows = cursor.fetchall()
for row in rows:
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    for item in itens:
        cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
---
Problem : Para cada pedido, são executadas 1 query de itens + N queries de nome de produto,
          resultando em 1 + P + (P×I) queries no total (P=pedidos, I=itens médios). A mesma
          estrutura se repete em get_todos_pedidos(). Com volume de dados em produção, isso
          causa degradação severa de performance e sobrecarga no banco.
Action  : Substituir pelas queries JOIN equivalentes:
          SELECT p.*, ip.*, pr.nome FROM pedidos p
          JOIN itens_pedido ip ON ip.pedido_id = p.id
          JOIN produtos pr ON pr.id = ip.produto_id
          WHERE p.usuario_id = ?

----------------------------------------------------------------

[MEDIUM] AP-09 — Code Duplication / Missing DRY
File    : controllers.py
Lines   : múltiplos (24–62, 64–96, e todas as funções)
---
    except Exception as e:
        print("ERRO: " + str(e))
        return jsonify({"erro": str(e)}), 500
---
Problem : O bloco try/except com retorno de erro 500 é duplicado em todas as 14 funções do
          controllers.py. A lógica de validação de produto (nome, preço, estoque, categoria)
          é duplicada entre criar_produto e atualizar_produto (≈20 linhas idênticas). O código
          de busca e serialização de pedidos com itens é idêntico em get_pedidos_usuario e
          get_todos_pedidos.
Action  : Extrair um decorator @handle_errors para o tratamento de exceções. Criar função
          _validar_produto_dados(dados) reutilizável. Criar _serializar_pedido_com_itens(row, cursor)
          para eliminar a duplicação nos dois métodos de listagem de pedidos.

----------------------------------------------------------------

[MEDIUM] AP-08 — Missing Input Validation at Route Level
File    : controllers.py
Lines   : 237–242
---
def atualizar_status_pedido(pedido_id):
    dados = request.get_json()
    novo_status = dados.get("status", "")
---
Problem : Se o body da request não for JSON válido, request.get_json() retorna None e a chamada
          dados.get() lança AttributeError (500 com stack trace exposto). Não há validação de
          formato de email em criar_usuario, nem de tipo numérico para preco/estoque. Nenhuma
          biblioteca de validação de schema (marshmallow, pydantic) está presente nas dependências.
Action  : Adicionar marshmallow ou pydantic para definir schemas de validação declarativos.
          No mínimo imediato: checar se request.get_json() retornou None antes de acessar campos.

----------------------------------------------------------------

[LOW] AP-10 — Magic Numbers and Magic Strings
File    : models.py
Lines   : 256–260
---
    if faturamento > 10000:
        desconto = faturamento * 0.1
    elif faturamento > 5000:
        desconto = faturamento * 0.05
    elif faturamento > 1000:
        desconto = faturamento * 0.02
---
Problem : Os thresholds de desconto (10000, 5000, 1000) e as taxas (0.1, 0.05, 0.02) são números
          literais sem nomes simbólicos. A lista de categorias válidas em controllers.py:52 também
          é uma magic list inline. Mudanças de regra de negócio exigem busca manual no código.
Action  : Definir constantes nomeadas: DESCONTO_TIER1_THRESHOLD = 10000,
          DESCONTO_TIER1_RATE = 0.10, etc. Extrair CATEGORIAS_VALIDAS para constants.py.

----------------------------------------------------------------

[LOW] AP-11 — Poor Naming / Semantic Misalignment
File    : models.py
Lines   : 1–314 (arquivo inteiro)
---
# models.py — contém apenas funções de acesso a banco (DAOs/Repository)
def get_todos_produtos(): ...
def criar_produto(...): ...
def login_usuario(...): ...
---
Problem : O arquivo models.py não contém modelos de domínio (classes com atributos e comportamento),
          mas sim funções de acesso a banco de dados — o papel semântico de um Repository ou DAO.
          A nomenclatura induz desenvolvedores a colocar lógica de domínio neste arquivo, reforçando
          o acoplamento entre domínio e persistência.
Action  : Renomear para repositories.py (ou criar pasta repositories/). Criar classes de modelo de
          domínio reais (Produto, Usuario, Pedido) separadas da lógica de persistência.


================================================================
Findings : 11 total
================================================================
