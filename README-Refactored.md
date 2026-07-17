## A) Análise Manual

Análise dos três projetos realizada antes da criação da skill, identificando problemas por severidade com justificativa arquitetural.

---

### Projeto 1 — `code-smells-project` (Python/Flask — API de E-commerce)

Arquivos originais: `app.py`, `controllers.py`, `models.py`, `database.py` (~781 linhas totais)

| # | Severidade | Arquivo / Linhas | Problema | Por que é relevante |
|---|-----------|-----------------|----------|---------------------|
| 1 | **CRITICAL** | `app.py:47–78` | **God Class**: `app.py` define rotas (`/admin/reset-db`, `/admin/query`) que acessam o banco diretamente inline, misturando bootstrap, roteamento e persistência no mesmo arquivo | Violação total de SRP: qualquer mudança no banco exige mexer no arquivo de inicialização; impossível testar rotas sem subir o banco completo |
| 2 | **CRITICAL** | `app.py:7–8` | **Credencial hardcoded**: `SECRET_KEY = "minha-chave-super-secreta-123"` e `DEBUG = True` literais no código | A SECRET_KEY assinada em JWT/sessões exposta no histórico git compromete a segurança de todos os usuários de forma irreversível |
| 3 | **CRITICAL** | `app.py:59–78` | **SQL Injection via endpoint aberto**: `/admin/query` aceita SQL arbitrário do body e executa sem autenticação ou sanitização | Backdoor completo — qualquer cliente HTTP pode executar `DROP TABLE`, `SELECT` em dados sensíveis ou criar usuário admin |
| 4 | **CRITICAL** | `models.py:105–111` | **SQL Injection na autenticação**: query de login montada por concatenação de strings (`"... WHERE email='" + email + "'"`) | Um atacante pode fazer bypass completo de autenticação com `' OR '1'='1` no campo email |
| 5 | **HIGH** | `models.py:133–169` | **Fat Model**: validação de estoque, cálculo de total e orquestração de múltiplas entidades (`produtos`, `pedidos`, `itens_pedido`) dentro de funções de Model | Models devem apenas persistir dados; misturar regras de negócio torna impossível reutilizar ou testar a lógica sem banco real |
| 6 | **HIGH** | `database.py:4–11` | **Global Mutable State**: `db_connection` é variável global compartilhada com `check_same_thread=False` suprimindo a proteção nativa do SQLite | Race conditions silenciosas em ambiente multi-thread; uma conexão global não libera recursos entre requests |
| 7 | **MEDIUM** | `models.py:186–199` | **N+1 Query**: para cada pedido, uma query busca seus itens; para cada item, outra busca o nome do produto — padrão aninhado em loops | 10 pedidos com 5 itens = 61 queries; degrada linearmente com volume e é inaceitável em produção |
| 8 | **MEDIUM** | `controllers.py:118–121` | **Input sem validação**: `float(preco_min)` aplicado diretamente na query string sem try/except; `?preco_min=abc` resulta em HTTP 500 com stack trace exposto | Facilita reconhecimento de vulnerabilidades e expõe internos da aplicação para clientes não autorizados |
| 9 | **LOW** | `models.py:256–259` | **Magic Numbers**: limiares de desconto (`10000`, `5000`, `1000`) e multiplicadores (`0.1`, `0.05`, `0.02`) sem constantes nomeadas | Regra de negócio invisível; mudança de política exige caça manual por valores literais espalhados no código |
| 10 | **LOW** | `models.py:187,219` | **Poor Naming**: cursores nomeados `cursor2` e `cursor3` sem indicar qual entidade cada um consulta | Dificulta leitura e onboarding; um leitor não sabe sem execução mental qual cursor acessa itens e qual acessa produtos |

---

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express — LMS API)

Arquivos originais: `src/app.js`, `src/AppManager.js`, `src/utils.js` (~180 linhas totais)

| # | Severidade | Arquivo / Linhas | Problema | Por que é relevante |
|---|-----------|-----------------|----------|---------------------|
| 1 | **CRITICAL** | `src/AppManager.js:1–141` | **God Class**: `AppManager` acumula 6+ responsabilidades: inicialização do banco, seed, rotas HTTP, lógica de pagamento, gestão de usuários e logging de auditoria | Impossível testar qualquer camada de forma isolada sem subir banco e servidor HTTP completos |
| 2 | **CRITICAL** | `src/utils.js:1–7` | **Credenciais hardcoded**: senha de banco de produção (`"senha_super_secreta_prod_123"`) e chave live de gateway de pagamento (`"pk_live_1234567890abcdef"`) versionadas no git | Violação direta de PCI-DSS e LGPD; qualquer acesso ao repositório concede acesso pleno às credenciais de produção |
| 3 | **HIGH** | `src/AppManager.js:28–78` | **Fat Controller — Checkout**: handler HTTP de 50 linhas com validação, busca de curso, criação de usuário, aprovação de pagamento e log de auditoria aninhados em callbacks | Regra de negócio de pagamento (`cc.startsWith("4")`) não pode ser testada sem simular uma requisição HTTP completa |
| 4 | **HIGH** | `src/AppManager.js:80–129` | **Fat Controller — Relatório**: lógica de agregação financeira (receita por curso, lista de estudantes com valores pagos) embutida no handler HTTP com 49 linhas de callbacks aninhados | Impossível reutilizar a lógica de agregação em outro contexto (job assíncrono, exportação CSV) |
| 5 | **HIGH** | `src/utils.js:9–10` | **Global Mutable State**: `globalCache` e `totalRevenue` são variáveis mutáveis exportadas no escopo do módulo, compartilhadas entre todas as requisições | Em Node.js single-process, dados de um usuário ficam acessíveis para outros via o mesmo cache sem isolamento |
| 6 | **MEDIUM** | `src/AppManager.js:89–128` | **N+1 Query**: para N cursos com M matrículas cada, são executadas 1+N+(N×M×2) queries; com 10 cursos e 50 matrículas = ~1001 queries por request | Degrada linearmente com volume; tornando o endpoint de relatório financeiro inutilizável em produção |
| 7 | **MEDIUM** | `src/AppManager.js:29–35` | **Input sem validação**: validação apenas verifica presença de 4 campos sem validar tipo de `cid` (int), formato de email ou tamanho de `cc` | Criação silenciosa de usuários com senha vazia; campo de cartão aceita qualquer string |
| 8 | **LOW** | `src/AppManager.js:46` | **Magic String**: `cc.startsWith("4")` para identificar cartão Visa sem constante nomeada; `"PAID"` e `"DENIED"` repetidos sem enum | Regra de negócio de pagamento invisível; mudança de prefixo ou status exige busca manual |

---

### Projeto 3 — `task-manager-api` (Python/Flask — Task Manager)

Arquivos originais: `app.py`, `database.py`, `models/`, `routes/` (5 arquivos de rota), `services/`, `utils/` (~1161 linhas totais)

| # | Severidade | Arquivo / Linhas | Problema | Por que é relevante |
|---|-----------|-----------------|----------|---------------------|
| 1 | **CRITICAL** | `routes/task_routes.py:1–300` | **God Route File**: arquivo de 300 linhas com 5 responsabilidades distintas — roteamento HTTP, acesso direto ao ORM (`Task.query`), validação de entrada, lógica de negócio (cálculo de overdue) e serialização manual | Violação de SRP; impossível testar a lógica de overdue sem simular uma request HTTP |
| 2 | **CRITICAL** | `app.py:11–13` | **Credenciais hardcoded**: `SECRET_KEY = 'super-secret-key-123'` e `SQLALCHEMY_DATABASE_URI` literais no código-fonte | Exposição de chave de sessão no histórico git; se vazada, permite forjar qualquer sessão da aplicação |
| 3 | **CRITICAL** | `services/notification_service.py:7–10` | **Credenciais hardcoded**: `email_password = 'senha123'` e `email_user = 'taskmanager@gmail.com'` hardcoded no construtor do serviço | Credenciais SMTP de produção versionadas; qualquer acesso ao repositório permite usar a conta de email da aplicação |
| 4 | **CRITICAL** | `routes/user_routes.py:207–210` | **Token fake previsível**: `'fake-jwt-token-' + str(user.id)` como resposta de login; `user.to_dict()` inclui o hash MD5 da senha na resposta | Token trivialmente forjável; hash MD5 exposto facilita ataques de dicionário offline |
| 5 | **HIGH** | `routes/task_routes.py:12–63` | **Fat Route**: função `get_tasks()` de 51 linhas com cálculo de overdue, resolução de relacionamentos, serialização manual e condicionais aninhadas em 3 níveis — ignorando `Task.is_overdue()` e `Task.to_dict()` já existentes no model | Lógica de overdue duplicada em 6 pontos da codebase; mudança na definição exige editar 6 arquivos |
| 6 | **HIGH** | `routes/report_routes.py:12–101` | **Fat Route — Relatório**: função de 90 linhas calculando produtividade por usuário, contando overdue e agregando estatísticas dentro do handler HTTP | Impossível reutilizar ou testar a lógica de relatório sem simular uma request |
| 7 | **MEDIUM** | `routes/task_routes.py:41–57` | **N+1 Query**: para cada task, uma query busca `User` e outra busca `Category` — ignorando os relacionamentos ORM com `joinedload` disponíveis | Com 100 tasks = 201 queries por request; os relacionamentos já estão definidos no ORM e apenas precisam de eager loading |
| 8 | **MEDIUM** | `routes/task_routes.py`, `routes/user_routes.py`, `routes/report_routes.py` | **Código duplicado**: bloco de lógica de overdue copiado em 6 pontos; serialização manual de Task em 3 arquivos ignorando `Task.to_dict()` existente | Correção de bug em um ponto não propaga para os outros; campos diferem entre cópias, criando inconsistência silenciosa |
| 9 | **MEDIUM** | `routes/task_routes.py`, `routes/user_routes.py`, `routes/report_routes.py` | **API deprecated**: `Model.query.get(pk)` usado em 8 locais — deprecated no SQLAlchemy 2.x com `LegacyAPIWarning` em runtime | Bloqueia upgrade do Flask-SQLAlchemy; emite warnings em produção; será removido em versão futura |
| 10 | **LOW** | `routes/report_routes.py:24–28` | **Poor Naming**: variáveis `p1`, `p2`, `p3`, `p4`, `p5` para contagens de prioridade sem nome descritivo | Leitor não sabe que `p1` significa "contagem de tasks com prioridade crítica" sem ler todo o contexto circundante |

---

## B) Construção da Skill

### Estrutura do SKILL.md e dos arquivos de referência

O `SKILL.md` foi projetado como um **prompt orquestrador** de 3 fases sequenciais, não como documentação. Cada fase tem:
- Objetivo explícito em uma linha
- Instrução de quais arquivos de referência ler antes de agir
- Sequência numerada de passos concretos (sem ambiguidade de ordem)
- Output esperado em formato fixo (blocos delimitados por `================================`)
- Critério de parada ou condição de avanço explícita

Os cinco arquivos de referência têm responsabilidades únicas e não se sobrepõem:

| Arquivo | Propósito na skill |
|---------|-------------------|
| `project-analysis.md` | Heurísticas de detecção de stack (linguagem, framework, banco, arquitetura, domínio) |
| `antipatterns-catalog.md` | 12 anti-patterns com IDs (AP-01…AP-12), sinais de detecção agnósticos e exemplos em 4 stacks |
| `template_audit_report.md` | Formato exato do relatório: cabeçalho, executive summary, bloco por finding (severidade, arquivo, linhas, trecho, problema, ação) |
| `architecture_guidelines.md` | Estrutura de diretórios MVC alvo, responsabilidades de cada camada, checklist pós-refatoração |
| `refactoring-playbook.md` | 11 padrões de transformação (PT-01…PT-11) com código ANTES/DEPOIS e ordem de aplicação recomendada |

### Anti-patterns incluídos no catálogo e justificativas

| ID | Nome | Severidade | Por que foi incluído |
|----|------|-----------|----------------------|
| AP-01 | God Class / Monolith File | CRITICAL | Ocorre nos 3 projetos; é o anti-pattern raiz que impossibilita qualquer teste |
| AP-02 | Hardcoded Credentials / Secrets | CRITICAL | Encontrado em todos os projetos; risco de segurança imediato e irreversível (histórico git) |
| AP-03 | SQL Injection | CRITICAL | Encontrado em 2 projetos; vetor de ataque mais crítico de qualquer API com banco |
| AP-04 | Fat Controller | HIGH | Presente nos 3 projetos em diferentes camadas; gera duplicação e impossibilita testes de negócio |
| AP-05 | Hard Coupling / No DI | HIGH | Presente nos 3 projetos; raiz da impossibilidade de mock e testes unitários |
| AP-06 | Global Mutable State | HIGH | Race conditions silenciosas em multi-thread; presente nos projetos Python e Node |
| AP-07 | N+1 Query Problem | MEDIUM | Gargalo de performance que degrada linearmente; presente nos 3 projetos |
| AP-08 | Missing Input Validation | MEDIUM | HTTP 500 com stack trace exposto; presente nos 3 projetos |
| AP-09 | Code Duplication / Missing DRY | MEDIUM | Bugs se propagam em múltiplos pontos; presente nos 3 projetos |
| AP-10 | Magic Numbers and Strings | LOW | Dívida técnica acumulada; presente nos 3 projetos |
| AP-11 | Poor Naming | LOW | Onboarding lento e erros por má interpretação; presente nos 3 projetos |
| AP-12 | Deprecated API Usage | MEDIUM | Bloqueia upgrades; detectado no projeto 3 (SQLAlchemy `Model.query.get()`) |

### Como a skill garante agnósticidade de tecnologia

**1. Sinais de detecção por heurística, não por sintaxe específica**
O catálogo de anti-patterns descreve o sinal de forma abstrata ("query dentro de loop for") antes de mostrar exemplos em 4 stacks (Python, JavaScript, Java, Go). O agente aplica o padrão conceitual e adapta para a linguagem detectada na Fase 1.

**2. Fase 1 detecta a stack antes de qualquer análise**
A Fase 1 lê o arquivo de referência de análise de projeto e detecta linguagem, framework e versão. As fases seguintes recebem esse contexto explícito e adaptam nomenclatura, idiomas e convenções automaticamente.

**3. Fase 3 usa a stack detectada como parâmetro**
O `architecture_guidelines.md` descreve a estrutura alvo em termos de camadas (Model, Controller, Routes/View, Database, Bootstrap) sem fixar extensão de arquivo ou nome de pasta. O `refactoring-playbook.md` instrui explicitamente: *"adapte a sintaxe e os idiomas à stack do projeto sem alterar os princípios estruturais"*.

**4. Validação de boot adapta o comando à stack**
A Fase 3 determina o comando de inicialização correto para a stack detectada (`python app.py`, `node src/app.js`, etc.) em vez de usar um comando fixo.

### Desafios encontrados e como foram resolvidos

**Desafio 1 — Tamanho do SKILL.md vs. clareza de instrução**
Um SKILL.md muito curto era ambíguo; um muito longo perdia foco. Solução: o SKILL.md contém apenas o protocolo de execução (o quê fazer, em que ordem, qual output produzir). O conhecimento de domínio (heurísticas, exemplos, regras) foi movido para os 5 arquivos de referência.

**Desafio 2 — Garantir que a Fase 2 não modifica arquivos**
A instrução explícita "Nenhum arquivo do projeto deve ser criado ou modificado nesta fase" foi adicionada no início de cada fase onde não há modificação. A pausar para confirmação humana (`Phase 2 complete. Proceed? [y/n]`) criou uma barreira clara entre análise e ação.

**Desafio 3 — Projetos com organização parcial (Projeto 3)**
O `task-manager-api` já tinha `models/`, `routes/`, `services/` e `utils/`, mas os arquivos de rota acumulavam lógica de negócio. A skill precisava distinguir "estrutura existe mas está mal usada" de "estrutura ausente". Solução: o `architecture_guidelines.md` define responsabilidades por camada (não apenas nomes de pasta), permitindo à Fase 3 identificar que `routes/task_routes.py` de 300 linhas viola o contrato da camada de roteamento mesmo existindo no lugar certo.

**Desafio 4 — Relatório com findings exatos por arquivo e linha**
A Fase 2 inicialmente gerava findings com descrições genéricas. Solução: o `template_audit_report.md` exige campos obrigatórios (`File`, `Lines`, trecho de código de até 10 linhas, `Problem`, `Action`) e proíbe a criação de findings sem evidência de código — forçando o agente a ler os arquivos antes de reportar.

---

## C) Resultados

### Resumo dos relatórios de auditoria

| Projeto | Stack | Arquivos analisados | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---------|-------|---------------------|----------|------|--------|-----|-------|
| `code-smells-project` | Python/Flask 3.1.1 | 4 (~781 linhas) | 8 | 5 | 6 | 4 | **23** |
| `ecommerce-api-legacy` | Node.js/Express 4.18.2 | 7 (~180 linhas) | 2 | 4 | 3 | 2 | **11** |
| `task-manager-api` | Python/Flask 3.0.0 | 15 (~1161 linhas) | 5 | 3 | 7 | 2 | **17** |

### Comparação antes/depois

#### Projeto 1 — `code-smells-project`

**Antes (estrutura monolítica):**
```
code-smells-project/
├── app.py           # bootstrap + rotas admin com SQL inline
├── controllers.py   # ~300 linhas com lógica + notificações
├── models.py        # ~350 linhas com negócio + SQL concatenado
└── database.py      # conexão global mutável + seed com senhas plaintext
```

**Depois (MVC):**
```
code-smells-project/
├── app.py                           # bootstrap limpo (registro de blueprints)
├── .env.example                     # variáveis de ambiente documentadas
├── database/
│   └── connection.py                # conexão escopada por request via Flask g
├── models/
│   ├── produto.py                   # queries parametrizadas, serialização centralizada
│   ├── usuario.py
│   └── pedido.py
├── controllers/
│   ├── produto_controller.py        # lógica de negócio isolada, sem HTTP
│   ├── usuario_controller.py
│   ├── pedido_controller.py
│   ├── relatorio_controller.py
│   ├── system_controller.py
│   └── constants.py                 # CATEGORIAS_VALIDAS, STATUS_PEDIDO como frozenset
├── routes/
│   ├── produto_routes.py            # roteamento puro + validação de input
│   ├── usuario_routes.py
│   ├── pedido_routes.py
│   ├── relatorio_routes.py
│   ├── auth_routes.py
│   └── health_routes.py
└── services/
    └── notification_service.py      # side-effects isolados
```

#### Projeto 2 — `ecommerce-api-legacy`

**Antes:**
```
ecommerce-api-legacy/src/
├── app.js           # bootstrap
├── AppManager.js    # God Class: banco + rotas + negócio + pagamento + log (141 linhas)
└── utils.js         # credenciais hardcoded + estado global (cache, totalRevenue)
```

**Depois:**
```
ecommerce-api-legacy/src/
├── app.js                           # bootstrap limpo
├── config.js                        # lê process.env, zero hardcoded
├── database/
│   └── connection.js                # instância SQLite injetável
├── models/
│   ├── userModel.js
│   ├── courseModel.js
│   ├── enrollmentModel.js
│   ├── paymentModel.js
│   ├── auditModel.js
│   └── reportModel.js               # JOIN único substituindo N+1
├── controllers/
│   ├── checkoutController.js        # lógica de pagamento isolada
│   ├── reportController.js
│   ├── userController.js
│   └── constants.js                 # VISA_PREFIX, PAYMENT_STATUS enum
└── routes/
    ├── checkoutRoutes.js
    ├── reportRoutes.js
    ├── userRoutes.js
    └── healthRoutes.js
```

#### Projeto 3 — `task-manager-api`

**Antes (parcialmente organizado, mas com violações):**
```
task-manager-api/
├── app.py                # credenciais hardcoded
├── database.py
├── models/               # modelos ORM bem definidos, com to_dict() e is_overdue()
├── routes/               # 5 arquivos de rota com 300+ linhas, fat routes
│   ├── task_routes.py    # God Route: roteamento + negócio + serialização + validação
│   ├── report_routes.py  # agregação financeira inline
│   └── ...
├── services/             # NotificationService com credenciais hardcoded
└── utils/                # constantes definidas mas não importadas nas rotas
```

**Depois:**
```
task-manager-api/
├── app.py                # bootstrap limpo, lê .env
├── config.py             # os.environ.get() para SECRET_KEY, DATABASE_URI
├── database.py
├── models/               # mantidos; to_dict() e is_overdue() centralizados e usados
├── controllers/          # nova camada — lógica extraída das rotas
│   ├── task_controller.py
│   ├── user_controller.py
│   ├── category_controller.py
│   ├── report_controller.py
│   └── exceptions.py
├── routes/               # rotas enxutas: parse + validação + chamada ao controller
│   ├── task_routes.py
│   ├── user_routes.py
│   ├── category_routes.py
│   ├── report_routes.py
│   └── health_routes.py
├── services/             # NotificationService com injeção de config SMTP
└── utils/
    └── helpers.py        # constantes agora importadas e usadas nas rotas
```

### Checklists de validação

#### Projeto 1 — `code-smells-project`

**Fase 1 — Análise**
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.1.1)
- [x] Domínio da aplicação descrito corretamente (E-commerce API — produtos, pedidos, usuários)
- [x] Número de arquivos analisados condiz com a realidade (4 arquivos)

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (22 encontrados)
- [x] Detecção de APIs deprecated incluída (não aplicável neste projeto)
- [x] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para `.env.example` (sem hardcoded)
- [x] Models criados para abstrair dados com queries parametrizadas
- [x] Routes separadas por domínio para roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado nas rotas
- [x] Entry point limpo (`app.py` registra blueprints apenas)
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

#### Projeto 2 — `ecommerce-api-legacy`

**Fase 1 — Análise**
- [x] Linguagem detectada corretamente (JavaScript/Node.js)
- [x] Framework detectado corretamente (Express 4.18.2)
- [x] Domínio da aplicação descrito corretamente (LMS API — cursos, matrículas, pagamentos)
- [x] Número de arquivos analisados condiz com a realidade (7 arquivos)

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (11 encontrados)
- [x] Detecção de APIs deprecated incluída (não aplicável neste projeto)
- [x] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para `config.js` com `process.env` (sem hardcoded)
- [x] Models criados para abstrair acesso ao banco (6 models)
- [x] Routes separadas por domínio para roteamento HTTP
- [x] Controllers concentram a lógica de negócio
- [x] Error handling centralizado
- [x] Entry point limpo (`app.js` registra rotas apenas)
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

#### Projeto 3 — `task-manager-api`

**Fase 1 — Análise**
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.0.0)
- [x] Domínio da aplicação descrito corretamente (Task Manager API — tasks, usuários, categorias)
- [x] Número de arquivos analisados condiz com a realidade (15 arquivos)

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (16 encontrados)
- [x] Detecção de APIs deprecated incluída (AP-12: `Model.query.get()` em 8 locais)
- [x] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC (camada `controllers/` adicionada)
- [x] Configuração extraída para `config.py` com `os.environ.get()` (sem hardcoded)
- [x] Models mantidos e corretamente utilizados via `to_dict()` e `is_overdue()`
- [x] Routes enxutas (parse + validação + chamada ao controller)
- [x] Controllers concentram lógica de negócio extraída das rotas
- [x] Error handling centralizado com `controllers/exceptions.py`
- [x] Entry point limpo
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

###Screenshots das aplicações rodando após a refatoração

#### Projeto 1 — `code-smells-project`

```
http://localhost:5000/login

```

<img width="1079" height="569" alt="image" src="https://github.com/user-attachments/assets/653fe1a0-2fb3-4bfb-94b6-9be8a158f8d3" />


```
http://localhost:5000/health

```
<img width="1086" height="645" alt="health" src="https://github.com/user-attachments/assets/26965e6d-32d2-4b16-b5d5-e2bad8e0411c" />

```
http://localhost:5000/pedidos/criar (criar)

```

<img width="1419" height="820" alt="Captura de tela de 2026-07-08 13-09-43" src="https://github.com/user-attachments/assets/2fa65e5e-2cd9-4b61-9e5e-4f0a3a5e2075" />


```

http://localhost:5000/pedidos/listar (listar)

```
<img width="1419" height="820" alt="Captura de tela de 2026-07-08 13-07-36" src="https://github.com/user-attachments/assets/a7fa173b-74a4-4a3b-8a51-b6548a0a48a7" />


```

http://localhost:5000/produtos/criar

```

<img width="1430" height="572" alt="Captura de tela de 2026-07-08 12-36-26" src="https://github.com/user-attachments/assets/c1e251a1-c4cf-4032-b765-6512f729e69b" />

```

http://localhost:5000/produtos/listar

```

<img width="1419" height="820" alt="Captura de tela de 2026-07-08 13-07-36" src="https://github.com/user-attachments/assets/cc32a97a-f0e2-4279-92cc-08f6e7e4f3ee" />


```

http://localhost:5000/relatorios/vendas

```
<img width="1430" height="572" alt="Captura de tela de 2026-07-08 13-04-41" src="https://github.com/user-attachments/assets/42e74bd2-0c2c-4b6d-a4f7-0c78274ec53f" />


<img width="1448" height="357" alt="Captura de tela de 2026-07-08 13-11-01" src="https://github.com/user-attachments/assets/3a5410ba-8481-4087-98ae-be369695c8f3" />


#### Projeto 2 — ecommerce-api-legacy

```

http://localhost:3000/api/checkout

```

<img width="1448" height="561" alt="Captura de tela de 2026-07-08 17-53-00" src="https://github.com/user-attachments/assets/6851a78b-7173-45f3-84d8-73849614633d" />

```

http://localhost:3000/health

```

<img width="1448" height="561" alt="Captura de tela de 2026-07-08 17-58-14" src="https://github.com/user-attachments/assets/39eb082b-bd55-40d3-a3bb-b126da0da482" />

```

http://localhost:3000/api/admin/financial-report

```

<img width="1444" height="827" alt="Captura de tela de 2026-07-08 18-02-36" src="https://github.com/user-attachments/assets/0d6de911-6580-420c-824a-f051269e0df8" />

```

http://localhost:3000/api/users/1

```

<img width="1444" height="827" alt="Captura de tela de 2026-07-08 18-17-14" src="https://github.com/user-attachments/assets/1400c64a-8617-49a7-8483-dffadfd10f26" />

<img width="1480" height="103" alt="Captura de tela de 2026-07-08 18-17-47" src="https://github.com/user-attachments/assets/7cdb5ab6-db5e-4100-87b5-7dc19c539392" />

#### Projeto 3 — `task-manager-api`

```

http://localhost:5000/categories

```

<img width="1430" height="889" alt="Categorias" src="https://github.com/user-attachments/assets/d663342c-b468-49a4-9458-d4a531394069" />


```

http://localhost:5000/categories/create

```

<img width="1431" height="540" alt="categorias create" src="https://github.com/user-attachments/assets/ffbfbf57-4404-44fb-94f5-795d5397212a" />


```

http://localhost:5000/health

```

<img width="1411" height="430" alt="health task-manager" src="https://github.com/user-attachments/assets/7e62e68d-675f-45d8-86a2-6c92b11d0c46" />

```

http://localhost:5000/reports/summary

```

<img width="1432" height="901" alt="reports summary" src="https://github.com/user-attachments/assets/f66d2893-9f34-42d4-9cc1-4152b281f347" />

```

http://localhost:5000/reports/users/2

```

<img width="1355" height="582" alt="reports user" src="https://github.com/user-attachments/assets/84078f85-df2c-455e-95fb-70a6c4606c7e" />

```

http://localhost:5000/tasks

```

<img width="1427" height="896" alt="tasks" src="https://github.com/user-attachments/assets/720df328-5d5f-4c10-8b9c-cee80cec968f" />

```

http://localhost:5000/tasks/2

```

<img width="1426" height="603" alt="task search" src="https://github.com/user-attachments/assets/603555d8-5406-4798-99d0-54da0e2fcf0d" />

```

http://localhost:5000/tasks/search?status=pending

```

<img width="1433" height="903" alt="tasks status" src="https://github.com/user-attachments/assets/3c5718d8-4399-40c8-99d7-8a48e4b79ab9" />

```

http://localhost:5000/tasks/search?priority=2

```

<img width="1425" height="903" alt="task priority" src="https://github.com/user-attachments/assets/a4de63c0-90ce-44d6-952d-5728ebd46b6e" />

```

http://localhost:5000/tasks/stats

```

<img width="1426" height="570" alt="task stats" src="https://github.com/user-attachments/assets/3ef01731-c57a-40d4-9987-0be2a689c184" />


```

http://localhost:5000/tasks/create

```

<img width="1433" height="842" alt="tasks create" src="https://github.com/user-attachments/assets/b2d67815-ef41-4bc9-9956-1c6820e97fc7" />


```

http://localhost:5000/tasks/11

```

<img width="1428" height="889" alt="tasks put" src="https://github.com/user-attachments/assets/5978aae3-711b-4c6d-a5fd-62249f7cdc38" />

```

http://localhost:5000/users

```

<img width="1408" height="770" alt="users" src="https://github.com/user-attachments/assets/72a43201-70e4-49ec-9085-70aca2ac369e" />

<img width="1234" height="327" alt="image" src="https://github.com/user-attachments/assets/804d4c73-55be-4e35-815d-bbd701f8e0e8" />


### Observações sobre comportamento da skill em stacks diferentes

- **Python/Flask (Projeto 1 — monolito)**: a skill identificou corretamente todos os anti-patterns de um arquivo único. A Fase 3 criou toda a estrutura MVC do zero, incluindo a extração de 4 arquivos em ~15 módulos.

- **Node.js/Express (Projeto 2)**: a skill adaptou nomenclatura (`.js`, `require`, `process.env`, `module.exports`) e substituiu o `AppManager.js` monolítico por módulos separados sem instrução explícita de como nomear os arquivos — apenas seguindo as convenções da stack detectada.

- **Python/Flask (Projeto 3 — parcialmente organizado)**: o caso mais interessante. A skill identificou que a estrutura de pastas existia mas as responsabilidades estavam incorretamente distribuídas (rotas com 300 linhas de negócio). A Fase 3 adicionou a camada `controllers/` ausente e redistribuiu o código sem recriar o que já estava correto.

---

## D) Como Executar

### Pré-requisitos

- **Claude Code** instalado e configurado (`claude --version`)
- **Python 3.10+** com `pip` para os projetos Python/Flask
- **Node.js 18+** com `npm` para o projeto Node.js/Express
- Permissão de leitura e escrita no diretório do projeto alvo

### Executar a skill em cada projeto

#### Projeto 1 — `code-smells-project`

```bash
cd code-smells-project
pip install -r requirements.txt   # instalar dependências
claude "/refactor-arch"
```

Quando a Fase 2 exibir `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`, revise o relatório exibido e responda `y` para iniciar a Fase 3.

#### Projeto 2 — `ecommerce-api-legacy`

```bash
cd ecommerce-api-legacy
npm install                        # instalar dependências
claude "/refactor-arch"
```

#### Projeto 3 — `task-manager-api`

```bash
cd task-manager-api
pip install -r requirements.txt   # instalar dependências
claude "/refactor-arch"
```

### Como validar que a refatoração funcionou

#### 1. Verificar boot da aplicação

**Python/Flask:**
```bash
# Criar .env a partir do exemplo antes de iniciar
cp .env.example .env
python app.py
# Esperado: "Running on http://127.0.0.1:5000" sem erros ou tracebacks
```

**Node.js/Express:**
```bash
cp .env.example .env
node src/app.js
# Esperado: "Server running on port 3000" sem erros
```

#### 2. Verificar endpoints

**Projeto 1 — E-commerce (Flask, porta 5000):**
```bash
# Health check
curl -s http://localhost:5000/health | python3 -m json.tool

# Listar produtos
curl -s http://localhost:5000/produtos | python3 -m json.tool

# Criar produto
curl -s -X POST http://localhost:5000/produtos \
  -H "Content-Type: application/json" \
  -d '{"nome":"Notebook","descricao":"Laptop","preco":2999.99,"estoque":10,"categoria":"informatica"}' \
  | python3 -m json.tool

# Login
curl -s -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@loja.com","senha":"admin123"}' \
  | python3 -m json.tool
```

**Projeto 2 — LMS (Express, porta 3000):**
```bash
# Health check
curl -s http://localhost:3000/health | python3 -m json.tool

# Checkout
curl -s -X POST http://localhost:3000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"usr":"Teste","eml":"teste@email.com","pwd":"senha","c_id":1,"card":"4111111111111111"}' \
  | python3 -m json.tool

# Relatório financeiro
curl -s http://localhost:3000/api/admin/financial-report | python3 -m json.tool
```

**Projeto 3 — Task Manager (Flask, porta 5000):**
```bash
# Health check
curl -s http://localhost:5000/health | python3 -m json.tool

# Listar tasks
curl -s http://localhost:5000/tasks | python3 -m json.tool

# Criar usuário e login
curl -s -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Teste","email":"teste@email.com","password":"senha123","role":"user"}' \
  | python3 -m json.tool

# Relatório resumido
curl -s http://localhost:5000/reports/summary | python3 -m json.tool
```

#### 3. Confirmar ausência de secrets hardcoded

```bash
# Verificar que nenhum secret ficou no código-fonte
grep -rn "secret\|password\|senha\|api_key\|token" \
  --include="*.py" --include="*.js" \
  --exclude-dir=".env" --exclude-dir="venv" --exclude-dir=".venv" \
  --exclude-dir="node_modules" .
# Apenas referências a os.environ.get() ou process.env devem aparecer
```

#### 4. Confirmar estrutura MVC

```bash
# Verificar que a estrutura de diretórios esperada existe
ls models/ controllers/ routes/          # Python
ls src/models/ src/controllers/ src/routes/  # Node.js
```
