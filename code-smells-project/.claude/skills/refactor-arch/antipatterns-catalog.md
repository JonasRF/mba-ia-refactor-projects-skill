# Anti-Patterns Catalog — Phase 2 Reference

Este arquivo define o catálogo oficial de anti-patterns usado pela skill `refactor-arch` na
**Fase 2 (Auditoria)**. Para cada anti-pattern são descritos: sinais de detecção no código-fonte,
severidade, impacto e exemplos representativos.

> **Stack coverage:** Python · JavaScript/TypeScript (Node.js) · Java · Go
> Os sinais de detecção e exemplos cobrem todas as stacks acima. Adapte os padrões de regex
> conforme a linguagem do projeto auditado.

---

## Escala de Severidade

| Nível    | Critério geral                                                                                                                                              |
|----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| CRITICAL | Falhas graves de arquitetura ou segurança: expõem dados sensíveis, permitem ataques, ou violam completamente a separação de responsabilidades em um único ponto do código. |
| HIGH     | Violações fortes de MVC ou SOLID que dificultam muito manutenção e testes, mesmo sem risco de segurança imediato.                                           |
| MEDIUM   | Problemas de padronização, duplicação ou gargalos de performance moderada que degradam a qualidade ao longo do tempo.                                       |
| LOW      | Melhorias de legibilidade, nomenclatura ou clareza que não bloqueiam manutenção mas acumulam dívida técnica.                                                |

---

## AP-01 — God Class / Monolith File

**Severidade:** `CRITICAL`

**Descrição:**
Um único arquivo ou classe concentra responsabilidades de banco de dados, lógica de negócio,
roteamento e inicialização da aplicação. Viola completamente o princípio Single Responsibility
(SRP) e impossibilita testes isolados de qualquer camada.

**Sinais de detecção (agnósticos):**

| Sinal | Heurística geral |
|-------|------------------|
| Rotas e queries no mesmo arquivo | Definição de endpoint HTTP + acesso direto a banco no mesmo escopo |
| Arquivo com >300 linhas misturando camadas | Imports de framework web, banco e lógica de domínio no mesmo arquivo |
| Inicialização de app e regras de negócio juntos | Configuração do servidor + cálculos de domínio no mesmo escopo global |
| Controller com acesso direto a banco | Método de controller contendo strings SQL ou chamadas ORM diretas |
| Classe com >5 responsabilidades distintas | Uma única classe lida com HTTP, persistência, validação, email e domínio |

**Exemplos por stack:**

```python
# Python / Flask — RUIM
app = Flask(__name__)
conn = sqlite3.connect("loja.db")

@app.route("/comprar", methods=["POST"])
def comprar():
    cur = conn.cursor()
    cur.execute("SELECT estoque FROM produtos WHERE id=?", (id,))
    if cur.fetchone()[0] < qty:
        return "Sem estoque", 400
    cur.execute("UPDATE produtos SET estoque=estoque-? WHERE id=?", (qty, id))
    conn.commit()
```

```javascript
// Node.js / Express — RUIM
const express = require('express');
const db = require('./db');
const app = express();

app.post('/comprar', async (req, res) => {
  const [produto] = await db.query('SELECT estoque FROM produtos WHERE id = ?', [req.body.id]);
  if (produto.estoque < req.body.qty) return res.status(400).send('Sem estoque');
  await db.query('UPDATE produtos SET estoque = estoque - ? WHERE id = ?', [req.body.qty, req.body.id]);
  res.send('OK');
});
```

```java
// Java / Spring — RUIM
@RestController
public class CompraController {
    @Autowired private JdbcTemplate jdbc;

    @PostMapping("/comprar")
    public ResponseEntity<?> comprar(@RequestBody CompraRequest req) {
        Integer estoque = jdbc.queryForObject(
            "SELECT estoque FROM produtos WHERE id = ?", Integer.class, req.getId());
        if (estoque < req.getQty()) return ResponseEntity.badRequest().body("Sem estoque");
        jdbc.update("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", req.getQty(), req.getId());
        return ResponseEntity.ok("OK");
    }
}
```

```go
// Go / net-http — RUIM
func comprarHandler(w http.ResponseWriter, r *http.Request) {
    var estoque int
    db.QueryRow("SELECT estoque FROM produtos WHERE id = $1", id).Scan(&estoque)
    if estoque < qty {
        http.Error(w, "Sem estoque", http.StatusBadRequest)
        return
    }
    db.Exec("UPDATE produtos SET estoque = estoque - $1 WHERE id = $2", qty, id)
}
```

**Impacto:** Impossível testar rotas sem banco real; mudança em qualquer camada exige editar o
mesmo arquivo; impossível reutilizar lógica de negócio em outros contextos.

---

## AP-02 — Hardcoded Credentials / Secrets in Source

**Severidade:** `CRITICAL`

**Descrição:**
Senhas, tokens de API, chaves secretas ou strings de conexão com banco de dados escritas
diretamente no código-fonte. Qualquer commit expõe as credenciais no histórico git e em
repositórios públicos.

**Sinais de detecção (agnósticos):**

| Sinal | Heurística geral |
|-------|------------------|
| Senha em string literal | Variável nomeada `password`, `secret`, `passwd` atribuída a string fixa |
| String de conexão com credencial | URL de banco com usuário e senha embutidos no código |
| Token de API literal | `api_key`, `token`, `bearer` atribuídos a string fixa |
| Chave JWT hardcoded | Segredo de assinatura JWT como string literal na chamada de encode/sign |
| Chave em arquivo de configuração versionado | Arquivo `config.*` ou `application.*` comitado contendo secrets reais |

**Exemplos por stack:**

```python
# Python — RUIM
SECRET_KEY = "minha-chave-super-secreta"
DATABASE_URL = "postgresql://admin:senha123@localhost/prod"
jwt.encode(payload, "chave_jwt_hardcoded", algorithm="HS256")
```

```javascript
// Node.js — RUIM
const SECRET = "minha-chave-super-secreta";
const DB_URL = "mongodb://admin:senha123@localhost/prod";
jwt.sign(payload, "chave_jwt_hardcoded");
```

```java
// Java — RUIM
private static final String SECRET = "minha-chave-super-secreta";
private static final String DB_URL = "jdbc:postgresql://admin:senha123@localhost/prod";
Jwts.builder().signWith(Keys.hmacShaKeyFor("chave_jwt_hardcoded".getBytes()));
```

```go
// Go — RUIM
const secret = "minha-chave-super-secreta"
db, _ := sql.Open("postgres", "postgres://admin:senha123@localhost/prod")
token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
token.SignedString([]byte("chave_jwt_hardcoded"))
```

**Regex de busca (multi-linguagem):**
```
(password|passwd|secret|api_key|token|secret_key|DATABASE_URL)\s*[:=]\s*["'][^"'$\{\s]{4,}["']
```

**Impacto:** Exposição de credenciais de produção; risco de comprometimento total do sistema;
violação de conformidade (LGPD, PCI-DSS, SOC2).

---

## AP-03 — SQL Injection (Concatenação Direta)

**Severidade:** `CRITICAL`

**Descrição:**
Construção de queries SQL por concatenação ou interpolação direta de entrada do usuário em vez de
usar parâmetros/placeholders. Permite ao atacante alterar a estrutura da query e acessar ou
destruir dados arbitrários.

**Sinais de detecção (agnósticos):**

| Sinal | Heurística geral |
|-------|------------------|
| Interpolação de variável em string SQL | Template string / format / concatenação misturando SQL e input do usuário |
| Ausência de placeholder parametrizado | Chamada de `execute` / `query` sem array/tupla de parâmetros separados |
| Concatenação de variáveis de request em SQL | `+`, `%`, `${}`, `fmt.Sprintf` unindo SQL com `req.*` / `params.*` / `args.*` |

**Exemplos por stack:**

```python
# Python — RUIM
query = f"SELECT * FROM usuarios WHERE nome='{nome}'"
cursor.execute("SELECT * FROM t WHERE id=" + id)
cursor.execute("SELECT * FROM t WHERE x='%s'" % valor)

# Python — BOM
cursor.execute("SELECT * FROM usuarios WHERE nome = %s", (nome,))
```

```javascript
// Node.js — RUIM
db.query(`SELECT * FROM usuarios WHERE nome = '${nome}'`);
db.query("SELECT * FROM t WHERE id = " + id);

// Node.js — BOM
db.query("SELECT * FROM usuarios WHERE nome = ?", [nome]);
```

```java
// Java — RUIM
String sql = "SELECT * FROM usuarios WHERE nome = '" + nome + "'";
stmt.executeQuery(sql);

// Java — BOM
PreparedStatement ps = conn.prepareStatement("SELECT * FROM usuarios WHERE nome = ?");
ps.setString(1, nome);
```

```go
// Go — RUIM
query := fmt.Sprintf("SELECT * FROM usuarios WHERE nome = '%s'", nome)
db.Query(query)

// Go — BOM
db.Query("SELECT * FROM usuarios WHERE nome = $1", nome)
```

**Regex de busca (multi-linguagem):**
```
# Python
cursor\.execute\(.*?[+%f].*?(request\.|input|param|arg|data\[)
execute\(f["'].*?\{

# JavaScript / TypeScript
db\.(query|execute)\(`[^`]*\$\{
db\.(query|execute)\(.*?\+.*?(req\.|params\.|body\.)

# Java
executeQuery\(.*?\+.*
executeUpdate\(.*?\+.*

# Go
(db|tx)\.(Query|Exec)\(fmt\.Sprintf
```

**Impacto:** Permite exfiltração total do banco, deleção de dados, bypass de autenticação e, em
alguns bancos, execução de comandos no servidor.

---

## AP-04 — Fat Controller (Business Logic in Controller)

**Severidade:** `HIGH`

**Descrição:**
Controllers contêm regras de negócio complexas que deveriam pertencer à camada de Service ou
Domain. O controller deixa de ser um coordenador fino (receber request → chamar serviço → devolver
response) e passa a executar cálculos, validações de domínio, transformações e orquestrações.

**Sinais de detecção (agnósticos):**

| Sinal | Heurística geral |
|-------|------------------|
| Método de controller com >30 linhas | Função de rota longa com múltiplos blocos condicionais de negócio |
| Cálculos de domínio no controller | Fórmulas de preço, desconto, frete ou pontuação dentro do handler HTTP |
| Orquestração de múltiplos modelos sem service | Controller instancia e coordena 3+ entidades/modelos diretamente |
| Formatação de dados de domínio no controller | Loops de transformação de objetos dentro da função de rota |
| Condicionais de negócio aninhadas no controller | Mais de 2 níveis de if/else com regras não relacionadas à request |

**Exemplos por stack:**

```python
# Python / Flask — RUIM
@app.route("/checkout", methods=["POST"])
def checkout():
    cliente = Cliente.query.get(request.json["cliente_id"])
    desconto = 0.1 if cliente.vip else 0
    total = sum(item["preco"] * item["qty"] for item in request.json["itens"])
    total = total * (1 - desconto)
    if total > 1000:
        total -= 50  # desconto progressivo
    pedido = Pedido(cliente_id=cliente.id, total=total)
    db.session.add(pedido)
    db.session.commit()
    # ... mais 20 linhas de lógica
```

```typescript
// Node.js / Express — RUIM
app.post('/checkout', async (req, res) => {
  const cliente = await Cliente.findById(req.body.clienteId);
  const desconto = cliente.vip ? 0.1 : 0;
  const total = req.body.itens.reduce((acc, i) => acc + i.preco * i.qty, 0) * (1 - desconto);
  const pedido = await Pedido.create({ clienteId: cliente.id, total });
  // ... mais 20 linhas de lógica
  res.json(pedido);
});
```

```java
// Java / Spring — RUIM
@PostMapping("/checkout")
public ResponseEntity<?> checkout(@RequestBody CheckoutRequest req) {
    Cliente cliente = clienteRepo.findById(req.getClienteId()).orElseThrow();
    double desconto = cliente.isVip() ? 0.1 : 0;
    double total = req.getItens().stream()
        .mapToDouble(i -> i.getPreco() * i.getQty()).sum() * (1 - desconto);
    // ... mais 20 linhas de lógica
}
```

```go
// Go — RUIM
func checkoutHandler(w http.ResponseWriter, r *http.Request) {
    // busca cliente, calcula desconto, calcula total, persiste pedido —
    // tudo dentro do handler, 50+ linhas
}
```

**Impacto:** Impossível testar regras de negócio sem simular uma requisição HTTP; duplicação de
lógica quando a mesma regra é necessária em outro endpoint; alta fricção para mudanças de negócio.

---

## AP-05 — Hard Coupling / No Dependency Injection

**Severidade:** `HIGH`

**Descrição:**
Classes e módulos instanciam suas dependências internamente em vez de recebê-las via injeção.
Viola o princípio Dependency Inversion (DIP) e torna substituição, mock e teste unitário
praticamente impossíveis.

**Sinais de detecção (agnósticos):**

| Sinal | Heurística geral |
|-------|------------------|
| Instanciação hardcoded de dependência no construtor | `new ConcreteService()` / `ConcreteRepo()` dentro do `__init__` / construtor de outro serviço |
| Import e uso direto de módulo de infraestrutura | Módulo de banco, email ou fila importado e chamado diretamente na camada de negócio |
| Singleton global de conexão usado em múltiplas camadas | Objeto de conexão criado no escopo global e importado em toda a aplicação |
| Ausência de interfaces ou contratos abstratos | Nenhum `Protocol`, `ABC`, `interface`, `trait` nos arquivos de serviço |
| Acoplamento a implementação concreta nomeada | Dependência declarada com tipo concreto em vez de tipo abstrato/interface |

**Exemplos por stack:**

```python
# Python — RUIM
class PedidoService:
    def __init__(self):
        self.repo = PedidoRepository()      # acoplado à implementação concreta
        self.email = SMTPEmailService()     # impossível trocar por mock

# Python — BOM
class PedidoService:
    def __init__(self, repo: PedidoRepositoryProtocol, email: EmailServiceProtocol):
        self.repo = repo
        self.email = email
```

```typescript
// Node.js / TypeScript — RUIM
class PedidoService {
  private repo = new PedidoRepository();       // acoplado
  private email = new SMTPEmailService();      // acoplado
}

// Node.js / TypeScript — BOM
class PedidoService {
  constructor(private repo: IPedidoRepository, private email: IEmailService) {}
}
```

```java
// Java / Spring — RUIM
@Service
public class PedidoService {
    private PedidoRepository repo = new PedidoRepository(); // ignora IoC container

// Java / Spring — BOM
@Service
public class PedidoService {
    private final PedidoRepository repo;
    public PedidoService(PedidoRepository repo) { this.repo = repo; }
}
```

```go
// Go — RUIM
func NewPedidoService() *PedidoService {
    return &PedidoService{repo: NewPedidoRepository()} // acoplado

// Go — BOM
func NewPedidoService(repo PedidoRepositoryInterface) *PedidoService {
    return &PedidoService{repo: repo}
}
```

**Impacto:** Testes exigem infraestrutura real; troca de implementação exige edição em múltiplos
pontos; viola Open/Closed Principle.

---

## AP-06 — Global Mutable State

**Severidade:** `HIGH`

**Descrição:**
Variáveis globais mutáveis são usadas para compartilhar estado entre diferentes partes da
aplicação. Em ambientes concorrentes causa race conditions; em qualquer ambiente dificulta rastrear
quando e onde o estado muda.

**Sinais de detecção (agnósticos):**

| Sinal | Heurística geral |
|-------|------------------|
| Variável global mutável modificada dentro de handlers | Coleção ou objeto no escopo do módulo que é lido e escrito por múltiplas rotas |
| Dicionário/mapa/lista global como "banco em memória" | Estrutura de dados global usada como substituto de persistência real |
| Estado de sessão em variável de módulo | Variável de sessão no topo do arquivo modificada por funções de rota |
| Uso explícito de `global` / variável de pacote mutável em handlers | Keyword `global` (Python) ou variável de pacote Go dentro de handler HTTP |
| Singleton mutável compartilhado sem sincronização | Objeto de estado compartilhado sem mutex/lock em ambiente concorrente |

**Exemplos por stack:**

```python
# Python — RUIM
carrinho = []   # estado global

@app.route("/adicionar", methods=["POST"])
def adicionar():
    global carrinho
    carrinho.append(request.json)  # race condition em multi-thread
```

```javascript
// Node.js — RUIM
let carrinho = [];  // estado global

app.post('/adicionar', (req, res) => {
  carrinho.push(req.body);  // compartilhado entre todas as requests
});
```

```java
// Java — RUIM
@RestController
public class CarrinhoController {
    private static List<Item> carrinho = new ArrayList<>(); // estado estático compartilhado

    @PostMapping("/adicionar")
    public void adicionar(@RequestBody Item item) {
        carrinho.add(item);  // não thread-safe
    }
}
```

```go
// Go — RUIM
var carrinho []Item  // variável de pacote global

func adicionarHandler(w http.ResponseWriter, r *http.Request) {
    // sem mutex — race condition em goroutines concorrentes
    carrinho = append(carrinho, parseItem(r))
}
```

**Impacto:** Race conditions em servidores multi-threaded; dados de um usuário vazam para outro;
impossível isolar testes; comportamento não-determinístico difícil de reproduzir.

---

## AP-07 — N+1 Query Problem

**Severidade:** `MEDIUM`

**Descrição:**
Para cada item de uma lista, uma query adicional é executada no banco — resultando em N+1 queries
no total. Tipicamente ocorre quando dados relacionados são carregados dentro de um loop em vez de
serem buscados com JOIN ou carregamento antecipado (eager loading).

**Sinais de detecção (agnósticos):**

| Sinal | Heurística geral |
|-------|------------------|
| Chamada de banco dentro de loop | `execute` / `query` / `findById` dentro de `for` / `forEach` / `range` |
| Busca por PK dentro de iteração sobre coleção | Lookup individual por ID para cada elemento de uma lista já carregada |
| Ausência de JOIN para relacionamentos carregados em loop | Query busca lista e depois acessa atributo relacionado item a item |
| Lazy loading implícito de ORM sem eager load configurado | Acesso a associação ORM dentro de loop sem `joinedload` / `include` / `fetch join` |

**Exemplos por stack:**

```python
# Python — RUIM
pedidos = db.execute("SELECT * FROM pedidos").fetchall()
for pedido in pedidos:
    itens = db.execute("SELECT * FROM itens WHERE pedido_id=?", (pedido["id"],)).fetchall()

# Python — BOM
pedidos = db.execute("""
    SELECT p.*, i.* FROM pedidos p
    JOIN itens i ON i.pedido_id = p.id
""").fetchall()
```

```typescript
// Node.js — RUIM
const pedidos = await Pedido.findAll();
for (const pedido of pedidos) {
  const itens = await Item.findAll({ where: { pedidoId: pedido.id } }); // N queries
}

// Node.js — BOM
const pedidos = await Pedido.findAll({ include: [{ model: Item }] }); // 1 query
```

```java
// Java / JPA — RUIM
List<Pedido> pedidos = pedidoRepo.findAll();
for (Pedido p : pedidos) {
    List<Item> itens = itemRepo.findByPedidoId(p.getId()); // N queries
}

// Java / JPA — BOM
// No repository:
@Query("SELECT p FROM Pedido p JOIN FETCH p.itens")
List<Pedido> findAllWithItens();
```

```go
// Go — RUIM
rows, _ := db.Query("SELECT * FROM pedidos")
for rows.Next() {
    var p Pedido
    rows.Scan(&p.ID)
    db.QueryRow("SELECT * FROM itens WHERE pedido_id = $1", p.ID).Scan(&p.Itens) // N queries
}

// Go — BOM
db.Query(`SELECT p.id, i.id, i.nome FROM pedidos p JOIN itens i ON i.pedido_id = p.id`)
```

**Impacto:** Performance degrada linearmente com volume de dados; tempo de resposta inaceitável
em produção; sobrecarga de conexões com o banco.

---

## AP-08 — Missing Input Validation at Route Level

**Severidade:** `MEDIUM`

**Descrição:**
Dados recebidos via request (body, query string, path params) são usados diretamente sem validação
de tipo, formato, presença ou domínio. Além do risco de segurança, erros internos do servidor (500)
vazam stack traces para o cliente.

**Sinais de detecção (agnósticos):**

| Sinal | Heurística geral |
|-------|------------------|
| Acesso direto a campos do body sem verificar presença | `request.body.campo` / `req.json["campo"]` sem checar existência |
| Cast sem tratamento de erro | Conversão de string para número sem capturar exceção de formato inválido |
| Ausência de biblioteca de validação de schema | Nenhum validator nas dependências (`pydantic`, `zod`, `joi`, `javax.validation`, etc.) |
| Ausência de schema ou DTO nos arquivos de rota | Controllers sem classe de request, DTO ou validator associado |
| Acesso por chave em coleção sem fallback | Indexação em dicionário/objeto sem `get()` / optional chaining / `?` |

**Exemplos por stack:**

```python
# Python — RUIM
nome = request.json["nome"]          # KeyError se ausente
id   = int(request.args.get("id"))   # ValueError se não for número

# Python — BOM (Pydantic)
class CompraInput(BaseModel):
    nome: str
    id: int

@app.post("/comprar")
def comprar(body: CompraInput): ...
```

```typescript
// Node.js — RUIM
const nome = req.body.nome;          // undefined se ausente
const id   = parseInt(req.query.id); // NaN sem validação

// Node.js — BOM (Zod)
const schema = z.object({ nome: z.string(), id: z.number() });
const body = schema.parse(req.body);
```

```java
// Java — RUIM
String nome = request.getParameter("nome"); // null sem validação
int id = Integer.parseInt(request.getParameter("id")); // NumberFormatException

// Java — BOM (Bean Validation)
public ResponseEntity<?> comprar(@Valid @RequestBody CompraRequest req) { ... }

public class CompraRequest {
    @NotBlank private String nome;
    @NotNull  private Integer id;
}
```

```go
// Go — RUIM
nome := r.FormValue("nome")          // string vazia sem validação
id, _ := strconv.Atoi(r.FormValue("id")) // erro silenciado

// Go — BOM
var req CompraRequest
if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
    http.Error(w, "Invalid body", http.StatusBadRequest)
    return
}
// validar campos obrigatórios explicitamente ou com biblioteca (go-playground/validator)
```

**Impacto:** Stack traces expostos ao cliente; crash em payloads inesperados; facilita exploração
de endpoints com dados malformados; dificulta contratos de API claros.

---

## AP-09 — Code Duplication / Missing DRY

**Severidade:** `MEDIUM`

**Descrição:**
Blocos de lógica idênticos ou muito similares repetidos em múltiplos locais sem extração para
função/método reutilizável. Viola o princípio Don't Repeat Yourself (DRY) e faz com que correções
precisem ser replicadas manualmente.

**Sinais de detecção (agnósticos):**

| Sinal | Heurística geral |
|-------|------------------|
| Bloco de conexão de banco repetido em múltiplos arquivos | Inicialização de conexão copiada em 3+ arquivos em vez de centralizada |
| Lógica de autenticação/autorização duplicada em rotas | Mesmo bloco de verificação de token copiado em múltiplas funções de rota |
| Serialização de objeto repetida | Mesmo mapeamento de campos construído manualmente em 2+ lugares |
| Query SQL idêntica em múltiplos controllers | Mesmo SELECT copiado em funções diferentes em vez de extraído para repositório |
| Tratamento de erro duplicado | Mesmo bloco try/catch/recover com mesma lógica repetido em múltiplos handlers |

**Exemplos por stack:**

```python
# Python — RUIM: mesma query em 3 controllers
# controller_a.py
conn = sqlite3.connect("db.sqlite")
cur = conn.cursor()
cur.execute("SELECT * FROM produtos WHERE id = ?", (id,))

# controller_b.py — cópia idêntica
conn = sqlite3.connect("db.sqlite")
cur = conn.cursor()
cur.execute("SELECT * FROM produtos WHERE id = ?", (id,))
```

```typescript
// Node.js — RUIM: verificação de token duplicada em cada rota
app.get('/pedidos', (req, res) => {
  if (!req.headers.authorization) return res.status(401).send('Unauthorized');
  // lógica ...
});
app.get('/produtos', (req, res) => {
  if (!req.headers.authorization) return res.status(401).send('Unauthorized');
  // lógica ... (cópia)
});

// Node.js — BOM: middleware reutilizável
const authMiddleware = (req, res, next) => {
  if (!req.headers.authorization) return res.status(401).send('Unauthorized');
  next();
};
app.get('/pedidos', authMiddleware, handler);
app.get('/produtos', authMiddleware, handler);
```

```java
// Java — RUIM: try/catch duplicado em todo controller
try {
    // lógica A
} catch (Exception e) {
    log.error(e.getMessage());
    return ResponseEntity.status(500).body("Erro interno");
}
// repetido em 10 métodos diferentes

// Java — BOM: @ControllerAdvice centraliza tratamento
@ControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(Exception.class)
    public ResponseEntity<?> handle(Exception e) { ... }
}
```

**Impacto:** Bugs corrigidos em um lugar mas não nos outros; manutenção multiplicada pelo número
de cópias; risco de divergência silenciosa entre cópias ao longo do tempo.

---

## AP-10 — Magic Numbers and Magic Strings

**Severidade:** `LOW`

**Descrição:**
Valores literais numéricos ou strings sem nome simbólico aparecem diretamente no código, sem
constantes nomeadas que expliquem seu significado. Dificulta leitura, manutenção e refatoração.

**Sinais de detecção (agnósticos):**

| Sinal | Heurística geral |
|-------|------------------|
| Números sem contexto em cálculos de domínio | Literal numérico em fórmula de negócio sem constante nomeada explicativa |
| Strings de status hardcoded e repetidas | `"ativo"`, `"admin"`, `"pendente"` repetidas em múltiplos arquivos |
| Códigos HTTP como número literal | `return 403` / `res.status(403)` em vez de constante nomeada |
| Limite de paginação sem constante | `LIMIT 20` / `pageSize = 20` hardcoded sem variável explicativa |
| Timeouts em segundos sem nome | `sleep(300)` / `setTimeout(fn, 300000)` sem constante `SESSION_TIMEOUT` |

**Exemplos por stack:**

```python
# Python — RUIM
if tentativas > 3: ...          # o que significa 3?
preco * 0.1                     # o que é 0.1?
return Response(body, 403)

# Python — BOM
MAX_LOGIN_ATTEMPTS    = 3
DESCONTO_VIP          = 0.10
return Response(body, HTTPStatus.FORBIDDEN)
```

```typescript
// Node.js — RUIM
setTimeout(logout, 300000);
if (role === "admin") { ... }

// Node.js — BOM
const SESSION_TIMEOUT_MS = 300_000;
const ROLE_ADMIN = "admin";
setTimeout(logout, SESSION_TIMEOUT_MS);
```

```java
// Java — RUIM
if (tentativas > 3) { ... }
return ResponseEntity.status(403).build();

// Java — BOM
private static final int MAX_TENTATIVAS = 3;
return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
```

```go
// Go — RUIM
time.Sleep(300 * time.Second)
if role == "admin" { ... }

// Go — BOM
const sessionTimeout = 300 * time.Second
const roleAdmin = "admin"
```

**Impacto:** Intenção do código não é clara para futuros leitores; mudança de valor requer busca
manual por todas as ocorrências; erros silenciosos ao atualizar apenas parte das ocorrências.

---

## AP-11 — Poor Naming / Semantic Misalignment

**Severidade:** `LOW`

**Descrição:**
Variáveis, funções ou classes com nomes genéricos (`data`, `obj`, `temp`, `x`), abreviações
obscuras ou nomes que não refletem o domínio de negócio real. Dificulta onboarding e raciocínio
sobre o código.

**Sinais de detecção (agnósticos):**

| Sinal | Heurística geral |
|-------|------------------|
| Variáveis de uma letra fora de loops curtos | `d`, `r`, `x`, `tmp` como variáveis de função com escopo amplo |
| Nomes genéricos para objetos de domínio | `process(data)` em vez de `processarPedido(pedido)` |
| Abreviações sem documentação | `calcDescCliVip()` sem docstring ou comentário explicativo |
| Funções com "and"/"e" no nome | `buscarESalvarProduto()` — indica múltiplas responsabilidades (viola SRP) |
| Nomes enganosos (cognatos falsos) | `usuarioAtivo` que retorna uma lista, não um booleano |

**Exemplos (independente de linguagem — padrão é o mesmo em todas):**

```
# RUIM — qualquer linguagem
def process(data): ...
function calc(x, y): ...
func handle(d interface{}): ...
void doStuff(Object obj): ...

# BOM — qualquer linguagem
def processar_pedido(pedido: Pedido): ...
function calcularDesconto(preco: number, cliente: Cliente): number { ... }
func processarPagamento(pagamento Pagamento) error { ... }
void aplicarDesconto(Pedido pedido, Cliente cliente): ...
```

**Impacto:** Tempo de leitura aumenta; novos desenvolvedores cometem erros por má interpretação;
code review torna-se mais lento.

---

## AP-12 — Deprecated API Usage

**Severidade:** `MEDIUM`

**Descrição:**
Uso de métodos, funções, classes ou configurações marcados como deprecated nas versões recentes do
framework ou da linguagem, ou que foram completamente removidos. Bloqueia upgrades e pode causar
quebras silenciosas em versões futuras.

> **Nota:** Esta seção deve ser mantida atualizada conforme os frameworks evoluem.
> Consulte os changelogs oficiais ao auditar versões específicas.

---

### Python

| API Deprecated | Substituição recomendada |
|----------------|--------------------------|
| `imp` module (removido 3.12) | `importlib` |
| `distutils` (removido 3.12) | `setuptools` |
| `asyncio.coroutine` decorator (removido 3.11) | `async def` nativo |
| `collections.Callable` (removido 3.10) | `collections.abc.Callable` |
| `typing.List` / `typing.Dict` (depreciado 3.9+) | `list[...]` / `dict[...]` nativos |

### Python / Flask

| API Deprecated | Substituição recomendada |
|----------------|--------------------------|
| `flask.ext.*` (Flask <1.0) | Importar diretamente do pacote (ex: `flask_sqlalchemy`) |
| `before_first_request` (removido Flask 2.3+) | `with app.app_context():` na inicialização |
| `SQLALCHEMY_TRACK_MODIFICATIONS = True` | Definir como `False` explicitamente |

### JavaScript / Node.js

| API Deprecated | Substituição recomendada |
|----------------|--------------------------|
| `require('url').parse()` | `new URL(...)` |
| `Buffer()` constructor | `Buffer.from()` / `Buffer.alloc()` |
| `fs.exists()` | `fs.access()` ou `fs.existsSync()` |
| `crypto.createCipher()` | `crypto.createCipheriv()` |
| Callbacks em APIs de `fs`, `http`, etc. | `fs.promises.*` / `util.promisify()` |
| `new Promise` envolvendo APIs já promisificadas | `await` direto nas APIs `fs.promises`, `dns.promises`, etc. |

### JavaScript / Express

| API Deprecated | Substituição recomendada |
|----------------|--------------------------|
| `res.send(statusCode)` com número (Express 4) | `res.sendStatus(statusCode)` |
| `req.param()` (Express 4) | `req.params`, `req.body` ou `req.query` conforme a origem |
| `app.del()` (Express 4) | `app.delete()` |
| `express.bodyParser()` (Express 4) | `express.json()` + `express.urlencoded()` |

### TypeScript

| API Deprecated | Substituição recomendada |
|----------------|--------------------------|
| `namespace` como substituto de módulos ES | Módulos ES nativos (`import` / `export`) |
| `/// <reference types="">` desnecessário | Configurar `types` no `tsconfig.json` |
| `Object` como tipo genérico | `unknown` ou tipo específico |

### Java

| API Deprecated | Substituição recomendada |
|----------------|--------------------------|
| `new Date()` / `Calendar` | `java.time.*` (LocalDate, LocalDateTime, ZonedDateTime) |
| `StringBuffer` em contexto single-thread | `StringBuilder` |
| `@RequestMapping(method=GET)` (verboso) | `@GetMapping`, `@PostMapping`, etc. |
| `EntityManager.createQuery(String)` sem tipo | `createQuery(String, Class<T>)` tipado |
| Spring `WebSecurityConfigurerAdapter` (removido 6.x) | `SecurityFilterChain` como bean |

### Go

| API Deprecated | Substituição recomendada |
|----------------|--------------------------|
| `ioutil.ReadAll` / `ioutil.WriteFile` (depreciado 1.16) | `io.ReadAll` / `os.WriteFile` |
| `ioutil.ReadDir` (depreciado 1.16) | `os.ReadDir` |
| `ioutil.TempFile` / `ioutil.TempDir` (depreciado 1.16) | `os.CreateTemp` / `os.MkdirTemp` |
| `rand.Seed` (depreciado 1.20) | Não necessário — gerador auto-seed global |
| `http.Get` sem contexto em serviços | `http.NewRequestWithContext` + timeout explícito |

---

### Regex de busca por linguagem

```regex
# Python
flask\.ext\.
before_first_request
\bimp\b\.
distutils
collections\.Callable
collections\.MutableMapping
asyncio\.coroutine

# JavaScript / Node.js
Buffer\(\s*[^.]
createCipher\(
req\.param\(
url\.parse\(
fs\.exists\(
res\.send\(\d{3}\)
app\.del\(

# Java
new Date\(\)(?!\.)           # uso de java.util.Date
Calendar\.getInstance
WebSecurityConfigurerAdapter
createQuery\(\"[^\"]+\"\)    # sem tipo genérico

# Go
ioutil\.(ReadAll|WriteFile|ReadDir|TempFile|TempDir)
rand\.Seed\(
```

**Impacto:** Warnings de deprecação em logs de produção; bloqueio de upgrade de versão; risco de
quebra ao atualizar o framework mesmo com bump de versão minor; comportamento silenciosamente
diferente entre versões.

---

## AP-13 — Weak / Reversible Password Hashing

**Severidade:** `CRITICAL`

**Descrição:**
Senhas de usuário são armazenadas com um algoritmo de hash rápido e sem salt (MD5, SHA-1, SHA-256
puro) em vez de uma função de derivação de chave projetada para senhas (bcrypt, scrypt, Argon2,
PBKDF2). Hashes rápidos são otimizados para velocidade, não para resistência a força bruta — um
vazamento do banco permite recuperar a maioria das senhas em minutos com hardware comum (GPU,
rainbow tables). Este anti-pattern é distinto de AP-02: não há credencial exposta em texto puro no
código-fonte, o problema é o algoritmo criptográfico usado para proteger a senha armazenada.

**Sinais de detecção (agnósticos):**

| Sinal | Heurística geral |
|-------|------------------|
| Hash de senha com algoritmo genérico rápido | `hashlib.md5`/`hashlib.sha1`/`hashlib.sha256` aplicado a senha, sem lib dedicada |
| Comparação manual de hash com `==` | `self.password == hash(pwd)` em vez de função de verificação com tempo constante |
| Ausência de salt explícito ou automático | Hash calculado apenas sobre o valor da senha, sem sal por usuário |
| Ausência de lib de hashing de senha nas dependências | Nenhum `bcrypt`, `argon2`, `passlib`, `werkzeug.security` no `requirements`/`package.json`/`pom.xml`/`go.mod` |
| Método `set_password`/`check_password`/`hash_password` reimplementado manualmente | Reimplementação própria de hashing em vez de biblioteca auditada |

**Exemplos por stack:**

```python
# Python — RUIM
import hashlib

def set_password(self, pwd):
    self.password = hashlib.md5(pwd.encode()).hexdigest()

def check_password(self, pwd):
    return self.password == hashlib.md5(pwd.encode()).hexdigest()

# Python — BOM
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, pwd):
    self.password = generate_password_hash(pwd)

def check_password(self, pwd):
    return check_password_hash(self.password, pwd)
```

```javascript
// Node.js — RUIM
const crypto = require('crypto');
const hash = crypto.createHash('md5').update(senha).digest('hex');

// Node.js — BOM
const bcrypt = require('bcrypt');
const hash = await bcrypt.hash(senha, 12);
const valido = await bcrypt.compare(senha, hash);
```

```java
// Java — RUIM
MessageDigest md = MessageDigest.getInstance("MD5");
byte[] hash = md.digest(senha.getBytes());

// Java — BOM (Spring Security)
PasswordEncoder encoder = new BCryptPasswordEncoder();
String hash = encoder.encode(senha);
boolean valido = encoder.matches(senha, hash);
```

```go
// Go — RUIM
h := md5.Sum([]byte(senha))
hash := hex.EncodeToString(h[:])

// Go — BOM
import "golang.org/x/crypto/bcrypt"
hash, _ := bcrypt.GenerateFromPassword([]byte(senha), bcrypt.DefaultCost)
err := bcrypt.CompareHashAndPassword(hash, []byte(senha))
```

**Regex de busca (multi-linguagem):**
```
hashlib\.(md5|sha1|sha256)\(.*?(pwd|password|senha)
createHash\((['"])(md5|sha1|sha256)\1\).*?(password|senha)
MessageDigest\.getInstance\(["'](MD5|SHA-1|SHA-256)["']\)
md5\.Sum\(|sha1\.Sum\(|sha256\.Sum256\(
```

**Impacto:** Vazamento do banco expõe a maioria das senhas em minutos via rainbow tables ou força
bruta em GPU; reuso de senha por usuários compromete outras contas/serviços; violação direta de
OWASP ASVS, LGPD e PCI-DSS.

---

## AP-14 — Fake or Predictable Authentication Token

**Severidade:** `CRITICAL`

**Descrição:**
O endpoint de login/autenticação devolve um "token" que não é criptograficamente gerado nem
verificável — construído por concatenação/interpolação de um dado previsível (ID do usuário,
contador, timestamp) em vez de um JWT assinado ou um identificador de sessão aleatório. Como o
valor é previsível e nenhuma rota valida assinatura ou existência real da sessão, qualquer cliente
consegue forjar acesso a qualquer conta apenas conhecendo (ou adivinhando) o ID do usuário.

**Sinais de detecção (agnósticos):**

| Sinal | Heurística geral |
|-------|------------------|
| Token construído por f-string/concatenação com ID | `f'token-{user.id}'`, `'session_' + str(id)`, `"Bearer:" + email` |
| Ausência de biblioteca de assinatura/geração segura | Nenhum `jwt`/`jsonwebtoken`/`jjwt`/`golang-jwt`, nenhum `secrets.token_*`/`crypto.randomBytes`/`SecureRandom` |
| Token sem expiração | Payload/valor de token sem campo `exp` ou TTL associado |
| Nenhuma verificação de token nas rotas protegidas | Rotas que deveriam exigir autenticação não decodificam nem validam o header `Authorization` |
| Token igual ou derivável a partir de dado público do usuário | Valor do token reconstruível apenas sabendo o ID/email, sem segredo do servidor |

**Exemplos por stack:**

```python
# Python — RUIM
return {"token": f"placeholder-{user.id}"}

# Python — BOM
import jwt, os
payload = {"sub": user.id, "role": user.role,
           "exp": datetime.now(timezone.utc) + timedelta(hours=8)}
token = jwt.encode(payload, os.environ["SECRET_KEY"], algorithm="HS256")
return {"token": token}
```

```javascript
// Node.js — RUIM
res.json({ token: `token-${user.id}` });

// Node.js — BOM
const jwt = require('jsonwebtoken');
const token = jwt.sign({ sub: user.id, role: user.role }, process.env.SECRET_KEY, { expiresIn: '8h' });
res.json({ token });
```

```java
// Java — RUIM
String token = "session-" + usuario.getId();

// Java — BOM (jjwt)
String token = Jwts.builder()
    .setSubject(String.valueOf(usuario.getId()))
    .setExpiration(Date.from(Instant.now().plus(8, ChronoUnit.HOURS)))
    .signWith(Keys.hmacShaKeyFor(secretKeyBytes))
    .compact();
```

```go
// Go — RUIM
token := fmt.Sprintf("token-%d", usuario.ID)

// Go — BOM
claims := jwt.MapClaims{"sub": usuario.ID, "exp": time.Now().Add(8 * time.Hour).Unix()}
token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
signed, _ := token.SignedString([]byte(os.Getenv("SECRET_KEY")))
```

**Regex de busca (multi-linguagem):**
```
token['"]?\s*[:=]\s*f?["'].*?\{.*?\.(id|user_id|email)
token['"]?\s*[:=]\s*["'].*?\+\s*(str\(|String\.valueOf\(|Sprintf).*?(id|Id|ID)
```

**Impacto:** Bypass completo de autenticação — qualquer atacante calcula ou adivinha o token de
qualquer usuário; nenhuma expiração ou revogação possível; comprometimento total de contas e dados
protegidos por login.

---
