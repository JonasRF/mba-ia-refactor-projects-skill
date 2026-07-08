# Architecture Audit Report

| | |
|---|---|
| **Project** | `ecommerce-api-legacy` |
| **Stack** | JavaScript (Node.js) + Express 4.18.2 |
| **Files** | 7 analyzed · ~180 lines of code |
| **Date** | 2026-06-26 |

---

## Executive Summary

This report presents the findings of a static architecture review of the `ecommerce-api-legacy` codebase. A total of **11 findings** were identified across 7 source files, ranging from critical security vulnerabilities — including hardcoded production credentials — to structural anti-patterns that compromise testability, maintainability, and scalability.

| Severity | Count | Status |
|:---|:---:|:---|
| 🔴 CRITICAL | 2 | Open |
| 🟠 HIGH | 4 | Open |
| 🟡 MEDIUM | 3 | Open |
| 🟢 LOW | 2 | Open |
| **Total** | **11** | |

---

## Findings

---

### 🔴 `AP-01` — God Class / Monolith File

| | |
|---|---|
| **File** | `src/AppManager.js` |
| **Lines** | 1–141 |

```js
class AppManager {
    constructor() {
        this.db = new sqlite3.Database(':memory:');
    }
    initDb() { /* CREATE TABLE + INSERT seeds */ }
    setupRoutes(app) {
        app.post('/api/checkout', (req, res) => { /* DB + negócio + pagamento */ });
        app.get('/api/admin/financial-report', (req, res) => { /* DB + agregação */ });
        app.delete('/api/users/:id', (req, res) => { /* DELETE sem cascata */ });
    }
}
```

**Problem**

A classe `AppManager` acumula 6+ responsabilidades distintas: inicialização do banco, seed de dados, definição de rotas HTTP, lógica de pagamento, gestão de usuários e logging de auditoria — tudo no mesmo arquivo. Impossível testar qualquer camada de forma isolada sem subir o banco e o servidor HTTP completos.

**Recommended Action**

Extrair cada responsabilidade para módulos dedicados: `Database` (conexão/schema), `Models/Repositories` (queries por entidade), `Controllers` (orquestração) e `Routes` (mapeamento HTTP). Apagar `AppManager` após a extração.

---

### 🔴 `AP-02` — Hardcoded Credentials / Secrets in Source

| | |
|---|---|
| **File** | `src/utils.js` |
| **Lines** | 1–7 |

```js
const config = {
    dbUser: "admin_master",
    dbPass: "senha_super_secreta_prod_123",
    paymentGatewayKey: "pk_live_1234567890abcdef",
    smtpUser: "no-reply@fullcycle.com.br",
    port: 3000
};
```

**Problem**

Senha de banco de produção e chave live do gateway de pagamento estão hardcoded no código-fonte e versionadas no git. Qualquer pessoa com acesso ao repositório tem acesso pleno às credenciais de produção — violação de PCI-DSS e LGPD.

**Recommended Action**

Remover todos os valores sensíveis do código. Criar arquivo `.env` (adicionado ao `.gitignore`) e ler via `process.env`: `PORT`, `DB_USER`, `DB_PASS`, `PAYMENT_GATEWAY_KEY`, `SMTP_USER`. Adicionar `.env.example` com chaves vazias para documentação.

---

### 🟠 `AP-04a` — Fat Controller — Checkout

| | |
|---|---|
| **File** | `src/AppManager.js` |
| **Lines** | 28–78 |

```js
app.post('/api/checkout', (req, res) => {
    // leitura de campos, validação parcial
    this.db.get("SELECT * FROM courses WHERE id = ?...", (err, course) => {
        this.db.get("SELECT id FROM users WHERE email = ?...", (err, user) => {
            let processPaymentAndEnroll = (userId) => {
                let status = cc.startsWith("4") ? "PAID" : "DENIED";
                this.db.run("INSERT INTO enrollments...", function(err) {
                    self.db.run("INSERT INTO payments...", function(err) {
                        self.db.run("INSERT INTO audit_logs...", (err) => {
                            logAndCache(...); res.status(200).json(...);
                        });
                    });
                });
            };
        });
    });
});
```

**Problem**

O handler do checkout concentra: validação de input, busca de curso, busca/criação de usuário, lógica de aprovação de pagamento (`cc.startsWith("4")`), criação de matrícula, criação de registro de pagamento e log de auditoria — tudo aninhado em 50 linhas de callbacks. A regra de negócio de pagamento não pode ser testada sem simular uma requisição HTTP completa.

**Recommended Action**

Extrair lógica de pagamento para `CheckoutController`/`CheckoutService`. Mover queries de user/course/enrollment/payment para seus respectivos `Models/Repositories`. O handler HTTP deve apenas parsear o body, chamar o service e mapear o resultado para status HTTP.

---

### 🟠 `AP-04b` — Fat Controller — Financial Report

| | |
|---|---|
| **File** | `src/AppManager.js` |
| **Lines** | 80–129 |

```js
app.get('/api/admin/financial-report', (req, res) => {
    this.db.all("SELECT * FROM courses", [], (err, courses) => {
        courses.forEach(c => {
            let courseData = { course: c.title, revenue: 0, students: [] };
            this.db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], (err, enrollments) => {
                enrollments.forEach(enr => {
                    this.db.get("SELECT name, email FROM users WHERE id = ?", [enr.user_id], ...);
                    this.db.get("SELECT amount, status FROM payments WHERE enrollment_id = ?", ...);
                });
            });
        });
    });
});
```

**Problem**

Lógica de agregação financeira (cálculo de receita por curso, montagem de lista de estudantes com valores pagos) está embutida diretamente no handler HTTP com 49 linhas de callbacks aninhados. Impossível reutilizar a lógica em outro contexto (ex: job assíncrono, exportação CSV).

**Recommended Action**

Extrair para `ReportController` e um método de agregação em `CourseModel`/`CourseRepository` (preferencialmente com JOIN). O handler deve apenas chamar o controller e serializar a resposta.

---

### 🟠 `AP-05` — Hard Coupling / No Dependency Injection

| | |
|---|---|
| **File** | `src/AppManager.js` |
| **Lines** | 4–8 |

```js
class AppManager {
    constructor() {
        this.db = new sqlite3.Database(':memory:');
    }
}
```

**Problem**

A conexão com o banco é instanciada diretamente dentro do construtor, acoplando `AppManager` à implementação concreta `sqlite3` e ao modo `:memory:`. Funções utilitárias são importadas diretamente pelo módulo. Nenhuma dependência é injetável, tornando mocking e substituição por banco real impossíveis.

**Recommended Action**

Criar módulo `database.js` que expõe a conexão. Injetar a instância de DB nos `Models` e `Controllers` via parâmetro de construtor ou argumento de função. Isso permite trocar `:memory:` por arquivo em teste/produção sem alterar o código de negócio.

---

### 🟠 `AP-06` — Global Mutable State

| | |
|---|---|
| **File** | `src/utils.js` |
| **Lines** | 9–10 |

```js
let globalCache = {};
let totalRevenue = 0;
```

**Problem**

`globalCache` é um objeto mutável no escopo do módulo, compartilhado entre todas as requisições simultâneas. Em Node.js (single-process, event-loop), dados de um usuário ficam acessíveis para outros via o mesmo cache em memória sem isolamento. `totalRevenue` é exportado mas nunca atualizado corretamente, criando estado morto e enganoso.

**Recommended Action**

Remover `globalCache` e `totalRevenue` do escopo de módulo. Se cache é necessário, usar Redis ou `Map` com escopo de request. Eliminar `totalRevenue` ou calculá-lo sob demanda via query agregada.

---

### 🟡 `AP-07` — N+1 Query Problem

| | |
|---|---|
| **File** | `src/AppManager.js` |
| **Lines** | 89–128 |

```js
courses.forEach(c => {
    this.db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], (err, enrollments) => {
        enrollments.forEach(enr => {
            this.db.get("SELECT name, email FROM users WHERE id = ?", [enr.user_id], (err, user) => {
                this.db.get("SELECT amount, status FROM payments WHERE enrollment_id = ?",
                    [enr.id], (err, payment) => { ... });
            });
        });
    });
});
```

**Problem**

Para N cursos com M matrículas cada, são executadas `1 + N + (N×M×2)` queries. Com 10 cursos e 50 matrículas médias, isso gera ~1001 queries por request do relatório financeiro. Degrada linearmente com o volume de dados.

**Recommended Action**

Substituir o padrão de loops+queries por uma única query com JOINs:

```sql
SELECT c.title, u.name, u.email, p.amount, p.status
FROM courses c
LEFT JOIN enrollments e ON e.course_id = c.id
LEFT JOIN users u      ON u.id = e.user_id
LEFT JOIN payments p   ON p.enrollment_id = e.id
```

Agregar em memória com uma única passagem sobre o resultado.

---

### 🟡 `AP-08` — Missing Input Validation at Route Level

| | |
|---|---|
| **File** | `src/AppManager.js` |
| **Lines** | 29–35 |

```js
let u   = req.body.usr;
let e   = req.body.eml;
let p   = req.body.pwd;
let cid = req.body.c_id;
let cc  = req.body.card;

if (!u || !e || !cid || !cc) return res.status(400).send("Bad Request");
```

**Problem**

A validação verifica apenas presença de 4 campos, sem validar: tipo de `cid` (deveria ser inteiro), formato de email em `e`, tamanho/formato de `cc` (campo de cartão). O campo `p` (senha) não é verificado na guarda, podendo criar usuários com senha fraca silenciosamente. Nenhuma biblioteca de validação de schema está no projeto.

**Recommended Action**

Adicionar biblioteca de validação (ex: `joi`, `zod`) e definir schema explícito para o body do checkout: `usr` (string, min 2), `eml` (email válido), `c_id` (integer positivo), `card` (string, min 13). Retornar erros de validação com detalhes em `422`.

---

### 🟡 `AP-09` — Code Duplication / Missing DRY

| | |
|---|---|
| **File** | `src/AppManager.js` |
| **Lines** | 41, 51, 55, 69, 83 |

```js
if (err) return res.status(500).send("Erro DB");
if (err) return res.status(500).send("Erro Matrícula");
if (err) return res.status(500).send("Erro Pagamento");
if (err) return res.status(500).send("Erro ao criar usuário");
if (err) return res.status(500).send("Erro DB");
```

**Problem**

O padrão de tratamento de erro de banco é repetido 5 vezes no mesmo arquivo com mensagens ligeiramente diferentes. Qualquer alteração no tratamento (ex: adicionar logging centralizado ou código de erro estruturado) exige editar 5 pontos distintos.

**Recommended Action**

Extrair função utilitária `handleDbError(err, res, message)` ou usar middleware de erro centralizado do Express. Cada callback de DB deve apenas chamar `next(err)` e deixar o middleware tratar o status `500`.

---

### 🟢 `AP-10` — Magic Numbers and Magic Strings

| | |
|---|---|
| **File** | `src/AppManager.js` · `src/utils.js` |
| **Lines** | `AppManager.js:46` · `utils.js:19–22` |

```js
// AppManager.js:46
let status = cc.startsWith("4") ? "PAID" : "DENIED";

// utils.js:19–22
for (let i = 0; i < 10000; i++) {
    hash += Buffer.from(pwd).toString('base64').substring(0, 2);
}
return hash.substring(0, 10);
```

**Problem**

`"4"` é o prefixo de cartão Visa sem nenhum comentário ou constante explicativa. `"PAID"` e `"DENIED"` são strings de status repetidas sem enum/constante. Na função `badCrypto`, `10000` (iterações), `2` (chars por bloco) e `10` (tamanho final do hash) são magic numbers sem semântica.

**Recommended Action**

Definir constantes nomeadas: `VISA_PREFIX = "4"`, `PAYMENT_STATUS = { PAID, DENIED }`, `HASH_ITERATIONS = 10000`, `HASH_BLOCK_SIZE = 2`, `HASH_LENGTH = 10`. Centralizar os status de pagamento em um módulo de enums/constantes.

---

### 🟢 `AP-11` — Poor Naming / Semantic Misalignment

| | |
|---|---|
| **File** | `src/AppManager.js` |
| **Lines** | 29–33 |

```js
let u   = req.body.usr;
let e   = req.body.eml;
let p   = req.body.pwd;
let cid = req.body.c_id;
let cc  = req.body.card;
```

**Problem**

Variáveis de letra única (`u`, `e`, `p`) e abreviações opacas (`cid`, `cc`) em escopo de função amplo (50 linhas). `processPaymentAndEnroll` viola SRP pelo nome ("and" indica múltiplas responsabilidades). `AppManager` não descreve suas responsabilidades reais.

**Recommended Action**

Renomear para: `userName`, `email`, `password`, `courseId`, `cardNumber`. Dividir `processPaymentAndEnroll` em `processPayment` e `createEnrollment`. Renomear `AppManager` para o módulo que realmente representa após a extração de camadas.

---
