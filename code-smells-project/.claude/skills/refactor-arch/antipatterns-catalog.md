# Anti-Patterns Catalog — Phase 2 Reference

Este arquivo define o catálogo oficial de anti-patterns usado pela skill `refactor-arch` na
**Fase 2 (Auditoria)**. Para cada anti-pattern são descritos: sinais de detecção no código-fonte,
severidade, impacto e exemplos representativos.

---

## Escala de Severidade

| Nível      | Critério geral                                                                                                  |
|------------|-----------------------------------------------------------------------------------------------------------------|
| CRITICAL   | Falhas graves de arquitetura ou segurança: expõem dados sensíveis, permitem ataques, ou violam completamente a separação de responsabilidades em um único ponto do código. |
| HIGH       | Violações fortes de MVC ou SOLID que dificultam muito manutenção e testes, mesmo sem risco de segurança imediato. |
| MEDIUM     | Problemas de padronização, duplicação ou gargalos de performance moderada que degradam a qualidade ao longo do tempo. |
| LOW        | Melhorias de legibilidade, nomenclatura ou clareza que não bloqueiam manutenção mas acumulam dívida técnica.     |

---

## AP-01 — God Class / Monolith File

**Severidade:** `CRITICAL`

**Descrição:**
Um único arquivo ou classe concentra responsabilidades de banco de dados, lógica de negócio,
roteamento e inicialização da aplicação. Viola completamente o princípio Single Responsibility
(SRP) e impossibilita testes isolados de qualquer camada.

**Sinais de detecção:**

| Sinal | Padrão / Heurística |
|-------|---------------------|
| Rotas e SQL no mesmo arquivo | `@app.route(` + `cursor.execute(` no mesmo arquivo `.py` / `.js` / `.rb` |
| Rotas e ORM no mesmo arquivo | `@app.route(` + `db.session` / `Model.query` no mesmo arquivo |
| Arquivo com >300 linhas misturando camadas | Arquivo único com imports de DB, framework web e lógica de domínio |
| Inicialização de app e regras de negócio juntos | `app = Flask(__name__)` + `if estoque < qty:` no mesmo escopo |
| Controller com acesso direto a banco | Método de controller contendo `SELECT`, `INSERT`, `UPDATE` em string SQL |

**Exemplo (Python/Flask):**
```python
# app.py — TUDO num arquivo só
app = Flask(__name__)
conn = sqlite3.connect("loja.db")

@app.route("/comprar", methods=["POST"])
def comprar():
    cur = conn.cursor()
    cur.execute("SELECT estoque FROM produtos WHERE id=?", (id,))
    # regra de negócio aqui dentro
    if cur.fetchone()[0] < qty:
        return "Sem estoque", 400
    cur.execute("UPDATE produtos SET estoque=estoque-? WHERE id=?", (qty, id))
    conn.commit()
```

**Impacto:** Impossível testar rotas sem banco real; mudança em qualquer camada exige editar o
mesmo arquivo; impossível reutilizar lógica em outros contextos.

---

## AP-02 — Hardcoded Credentials / Secrets in Source

**Severidade:** `CRITICAL`

**Descrição:**
Senhas, tokens de API, chaves secretas ou strings de conexão com banco de dados escritas
diretamente no código-fonte. Qualquer commit expõe as credenciais no histórico git e em
repositórios públicos.

**Sinais de detecção:**

| Sinal | Padrão / Heurística |
|-------|---------------------|
| Senha em string literal | `password = "minhasenha123"` / `SECRET_KEY = "abc123"` fora de `.env` |
| String de conexão com credencial | `"postgresql://user:senha@host/db"` hardcoded em `.py` / `.js` |
| Token de API literal | `api_key = "sk-..."` / `token = "Bearer eyJ..."` no código |
| Chave JWT hardcoded | `jwt.encode(payload, "chave_secreta", ...)` com string literal |
| Chave em configuração versionada | `SECRET_KEY = "dev-only-key"` em `config.py` comitado sem `.gitignore` |

**Regex de busca sugerido:**
```
(password|passwd|secret|api_key|token|secret_key)\s*=\s*["'][^"'$\{]{4,}["']
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

**Sinais de detecção:**

| Sinal | Padrão / Heurística |
|-------|---------------------|
| f-string / format em SQL | `f"SELECT * FROM usuarios WHERE nome='{nome}'"` |
| Concatenação de variável em SQL | `"SELECT * FROM " + tabela + " WHERE id=" + id` |
| `%s` com `%` (não como placeholder) | `"SELECT * FROM t WHERE x='%s'" % valor` |
| `.format()` em query SQL | `"SELECT * FROM t WHERE id={}".format(id)` |
| Falta de placeholder `?` / `%s` com tuple | `cursor.execute(query)` sem segundo argumento |

**Regex de busca sugerido:**
```
cursor\.execute\(.*?[+%].*?(request\.|input|param|arg|data\[)
execute\(f["'].*?\{
```

**Impacto:** Permite exfiltração total do banco, deleção de dados, bypass de autenticação e, em
alguns bancos, execução de comandos no servidor (via `xp_cmdshell` no SQL Server).

---

## AP-04 — Fat Controller (Business Logic in Controller)

**Severidade:** `HIGH`

**Descrição:**
Controllers contêm regras de negócio complexas que deveriam pertencer à camada de Service ou
Domain. O controller deixa de ser um coordenador fino (receber request → chamar serviço → devolver
response) e passa a executar cálculos, validações de domínio, transformações e orquestrações.

**Sinais de detecção:**

| Sinal | Padrão / Heurística |
|-------|---------------------|
| Métodos de controller com >30 linhas | Função de rota longa com múltiplos `if/else` de regra de negócio |
| Cálculos de domínio no controller | `desconto = preco * 0.1 if cliente.vip else 0` dentro de `@app.route` |
| Orquestração de múltiplos modelos sem service | Controller instancia e coordena 3+ modelos diretamente |
| Formatação de dados de domínio no controller | Loops de transformação de objetos dentro da função de rota |
| Regras condicionais de negócio aninhadas | Mais de 2 níveis de `if/elif/else` em lógica não relacionada à request |

**Impacto:** Impossível testar regras de negócio sem simular uma requisição HTTP; duplicação de
lógica quando a mesma regra é necessária em outro endpoint; alta fricção para mudanças de negócio.

---

## AP-05 — Hard Coupling / No Dependency Injection

**Severidade:** `HIGH`

**Descrição:**
Classes e módulos instanciam suas dependências internamente (com `new` / construtores diretos) em
vez de recebê-las via injeção. Viola o princípio Dependency Inversion (DIP) e torna substituição,
mock e teste unitário praticamente impossíveis.

**Sinais de detecção:**

| Sinal | Padrão / Heurística |
|-------|---------------------|
| Instanciação hardcoded de dependência | `self.repo = ProdutoRepository()` dentro do `__init__` de um Service |
| Import e uso direto de módulo de banco | `import database; database.get_connection()` dentro de lógica de negócio |
| Singleton global de conexão | `conn = sqlite3.connect("db.sqlite")` no escopo do módulo, importado em vários arquivos |
| Acoplamento a implementação concreta | `from email_service import SMTPEmailService` diretamente no controller |
| Ausência de interfaces / protocolos | Nenhum `Protocol`, `ABC`, `interface` ou tipo abstrato nos arquivos de serviço |

**Impacto:** Testes exigem banco real ou monkey-patching frágil; troca de implementação (ex:
mudar de SQLite para PostgreSQL) exige edição em múltiplos pontos; viola Open/Closed Principle.

---

## AP-06 — Global Mutable State

**Severidade:** `HIGH`

**Descrição:**
Variáveis globais mutáveis são usadas para compartilhar estado entre diferentes partes da
aplicação (ex: sessão, carrinho, configurações de runtime). Em ambientes concorrentes isso causa
race conditions; em qualquer ambiente dificulta rastrear quando e onde o estado muda.

**Sinais de detecção:**

| Sinal | Padrão / Heurística |
|-------|---------------------|
| Variável global mutável modificada em funções | `global carrinho; carrinho.append(item)` |
| Dicionário/lista global usada como "banco em memória" | `usuarios = {}` no escopo do módulo, lido e escrito por rotas |
| Estado de sessão em variável de módulo | `sessao_atual = None` no topo do arquivo, modificado por funções de rota |
| Configuração mutada em runtime | `config["debug"] = True` dentro de handler de requisição |
| `global` keyword dentro de funções de rota | Qualquer uso de `global` dentro de função decorada com `@app.route` |

**Impacto:** Race conditions em servidores multi-threaded (ex: Gunicorn); dados de um usuário
vazam para outro; impossível isolar testes; comportamento não-determinístico difícil de reproduzir.

---

## AP-07 — N+1 Query Problem

**Severidade:** `MEDIUM`

**Descrição:**
Para cada item de uma lista, uma query adicional é executada no banco — resultando em N+1 queries
no total. Tipicamente ocorre quando dados relacionados são carregados dentro de um loop em vez de
serem buscados com JOIN ou carregamento antecipado (eager loading).

**Sinais de detecção:**

| Sinal | Padrão / Heurística |
|-------|---------------------|
| `cursor.execute` dentro de `for` loop | Loop iterando sobre resultados de query e executando nova query por item |
| `.query.get(id)` / `.find_by_id(id)` dentro de loop | ORM query por PK dentro de iteração sobre coleção |
| Ausência de `JOIN` para relacionamentos | Query busca lista e depois acessa atributo relacionado item a item |
| `lazy loading` implícito em ORM sem eager load | Acesso a `pedido.itens` dentro de loop sem `joinedload` / `includes` / `with` |

**Exemplo (Python):**
```python
pedidos = db.execute("SELECT * FROM pedidos").fetchall()
for pedido in pedidos:
    # executa 1 query por pedido = N queries extras
    itens = db.execute("SELECT * FROM itens WHERE pedido_id=?", (pedido["id"],)).fetchall()
```

**Impacto:** Performance degrada linearmente com volume de dados; tempo de resposta inaceitável
em produção; sobrecarga de conexões com o banco.

---

## AP-08 — Missing Input Validation at Route Level

**Severidade:** `MEDIUM`

**Descrição:**
Dados recebidos via request (body, query string, path params) são usados diretamente sem validação
de tipo, formato, presença ou domínio. Além do risco de segurança (payload malformado), erros
internos do servidor (500) vazam stack traces para o cliente.

**Sinais de detecção:**

| Sinal | Padrão / Heurística |
|-------|---------------------|
| Acesso direto a `request.json` sem checar campos | `nome = request.json["nome"]` sem `.get()` ou try/except |
| Cast sem validação | `id = int(request.args.get("id"))` sem tratar `ValueError` |
| Ausência de biblioteca de validação | Nenhum `marshmallow`, `pydantic`, `joi`, `zod`, `cerberus` nas dependências |
| Nenhum schema de validação nos arquivos de rota | Arquivos de controller sem definição de schema ou validator |
| `KeyError` / `TypeError` possíveis no fluxo | Acesso por índice em dicionários sem `get()` ou validação prévia |

**Impacto:** Stack traces expostos ao cliente; crash em payloads inesperados; facilita exploração
de endpoints com dados malformados; dificulta contratos de API claros.

---

## AP-09 — Code Duplication / Missing DRY

**Severidade:** `MEDIUM`

**Descrição:**
Blocos de lógica idênticos ou muito similares repetidos em múltiplos locais (controllers,
funções, módulos) sem extração para função/método reutilizável. Viola o princípio Don't Repeat
Yourself (DRY) e faz com que correções precisem ser replicadas manualmente.

**Sinais de detecção:**

| Sinal | Padrão / Heurística |
|-------|---------------------|
| Blocos idênticos de conexão de banco em múltiplos arquivos | `conn = sqlite3.connect("db.sqlite")` repetido em 3+ arquivos |
| Lógica de autenticação/autorização duplicada em rotas | Mesmo bloco `if not token: return 401` copiado em múltiplas funções |
| Serialização de objeto repetida | Mesmo dicionário de campos construído manualmente em 2+ lugares |
| Query SQL idêntica em múltiplos controllers | Mesmo `SELECT * FROM produtos WHERE id=?` em funções diferentes |
| Tratamento de erro duplicado | Mesmo bloco `try/except` com mesma lógica repetido em múltiplos handlers |

**Impacto:** Bugs corrigidos em um lugar mas não nos outros; manutenção multiplicada pelo número
de cópias; aumenta risco de divergência silenciosa entre cópias ao longo do tempo.

---

## AP-10 — Magic Numbers and Magic Strings

**Severidade:** `LOW`

**Descrição:**
Valores literais numéricos ou strings sem nome simbólico aparecem diretamente no código, sem
constantes nomeadas que expliquem seu significado. Dificulta leitura, manutenção e refatoração.

**Sinais de detecção:**

| Sinal | Padrão / Heurística |
|-------|---------------------|
| Números sem contexto em cálculos | `preco * 0.1` (o que é 0.1?), `if tentativas > 3` (por que 3?) |
| Strings de status hardcoded | `status = "ativo"` / `tipo = "admin"` repetidas em múltiplos lugares |
| Códigos HTTP como número literal | `return Response(body, 403)` em vez de constante nomeada |
| Limite de paginação sem constante | `LIMIT 20` hardcoded em queries sem variável explicativa |
| Timeouts em segundos sem nome | `time.sleep(300)` sem constante `SESSION_TIMEOUT_SECONDS` |

**Impacto:** Intenção do código não é clara para futuros leitores; mudança de valor requer busca
manual por todas as ocorrências; erros silenciosos ao atualizar apenas parte das ocorrências.

---

## AP-11 — Poor Naming / Semantic Misalignment

**Severidade:** `LOW`

**Descrição:**
Variáveis, funções ou classes com nomes genéricos (`data`, `obj`, `temp`, `x`), abreviações
obscuras (`calcDesc`, `procPed`) ou nomes que não refletem o domínio de negócio real. Dificulta
onboarding e raciocínio sobre o código.

**Sinais de detecção:**

| Sinal | Padrão / Heurística |
|-------|---------------------|
| Variáveis de uma letra fora de loops curtos | `d`, `r`, `x`, `tmp` como variáveis de função |
| Nomes genéricos para objetos de domínio | `def process(data):` em vez de `def processar_pedido(pedido):` |
| Abreviações sem documentação | `calc_desc_cli_vip()` sem docstring ou comentário |
| Funções com "and" / "e" no nome | `buscar_e_salvar_produto()` — indica múltiplas responsabilidades |
| Nomes enganosos (false cognates) | `usuario_ativo` que retorna uma lista, não um booleano |

**Impacto:** Tempo de leitura aumenta; novos desenvolvedores cometem erros por má interpretação;
code review torna-se mais lento.

---

## Deprecated API Usage


**Descrição:**
Uso de métodos, funções, classes ou configurações que foram marcados como deprecated nas versões
recentes do framework ou da linguagem, ou que foram completamente removidos. Bloqueia upgrades e
pode causar quebras silenciosas em versões futuras.

**Sinais de detecção por stack:**

### Python / Flask
| API Deprecated | Substituição |
|----------------|-------------|
| `flask.ext.*` (Flask <1.0) | Importar diretamente do pacote (ex: `flask_sqlalchemy`) |
| `before_first_request` (removido Flask 2.3+) | Usar `with app.app_context():` na inicialização |
| `flask.json.provider` antigo (Flask <2.2) | Usar `app.json` do novo provider |
| `SQLALCHEMY_TRACK_MODIFICATIONS = True` (depreciado) | Definir como `False` explicitamente |
| `@app.teardown_request` sem `exc` param | Adicionar parâmetro `exc=None` obrigatório |

### Python geral
| API Deprecated | Substituição |
|----------------|-------------|
| `imp` module (removido Python 3.12) | `importlib` |
| `distutils` (removido Python 3.12) | `setuptools` |
| `asyncio.coroutine` decorator (removido Python 3.11) | `async def` nativo |
| `collections.Callable` (removido Python 3.10) | `collections.abc.Callable` |
| `typing.List` / `typing.Dict` (depreciado 3.9+) | `list[...]` / `dict[...]` nativos |

### JavaScript / Node.js
| API Deprecated | Substituição |
|----------------|-------------|
| `require('url').parse()` | `new URL(...)` |
| `Buffer()` constructor | `Buffer.from()` / `Buffer.alloc()` |
| `fs.exists()` | `fs.access()` ou `fs.existsSync()` |
| `crypto.createCipher()` | `crypto.createCipheriv()` |
| Express 4: `res.send(status)` com número | `res.sendStatus(status)` |
| Express 4: `req.param()` | `req.params`, `req.body`, `req.query` |

### Regex de busca genérico
```
flask\.ext\.
before_first_request
imp\.
distutils
collections\.Callable
collections\.MutableMapping
Buffer\(\s*[^.]
createCipher\(
req\.param\(
```

**Impacto:** Warnings de deprecação em logs de produção; bloqueio de upgrade de versão; risco de
quebra ao atualizar o framework mesmo com bump de versão minor; comportamento silenciosamente
diferente entre versões.

---