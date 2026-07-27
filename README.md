# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

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
| 5 | **CRITICAL** | `controllers.py:167–186` | **Autenticação inexistente**: `login()` retorna apenas `{"dados": usuario, "sucesso": True, "mensagem": "Login OK"}` — nenhum token, JWT ou identificador de sessão é gerado, e nenhuma rota da aplicação exige ou valida um header `Authorization` | Não existe controle de acesso real: qualquer cliente cria, atualiza ou deleta produtos e pedidos, ou lista usuários, sem nunca ter se autenticado de fato, mesmo após um "login" bem-sucedido |
| 6 | **HIGH** | `models.py:133–169` | **Fat Model**: validação de estoque, cálculo de total e orquestração de múltiplas entidades (`produtos`, `pedidos`, `itens_pedido`) dentro de funções de Model | Models devem apenas persistir dados; misturar regras de negócio torna impossível reutilizar ou testar a lógica sem banco real |
| 7 | **HIGH** | `database.py:4–11` | **Global Mutable State**: `db_connection` é variável global compartilhada com `check_same_thread=False` suprimindo a proteção nativa do SQLite | Race conditions silenciosas em ambiente multi-thread; uma conexão global não libera recursos entre requests |
| 8 | **MEDIUM** | `models.py:186–199` | **N+1 Query**: para cada pedido, uma query busca seus itens; para cada item, outra busca o nome do produto — padrão aninhado em loops | 10 pedidos com 5 itens = 61 queries; degrada linearmente com volume e é inaceitável em produção |
| 9 | **MEDIUM** | `controllers.py:118–121` | **Input sem validação**: `float(preco_min)` aplicado diretamente na query string sem try/except; `?preco_min=abc` resulta em HTTP 500 com stack trace exposto | Facilita reconhecimento de vulnerabilidades e expõe internos da aplicação para clientes não autorizados |
| 10 | **LOW** | `models.py:256–259` | **Magic Numbers**: limiares de desconto (`10000`, `5000`, `1000`) e multiplicadores (`0.1`, `0.05`, `0.02`) sem constantes nomeadas | Regra de negócio invisível; mudança de política exige caça manual por valores literais espalhados no código |
| 11 | **LOW** | `models.py:187,219` | **Poor Naming**: cursores nomeados `cursor2` e `cursor3` sem indicar qual entidade cada um consulta | Dificulta leitura e onboarding; um leitor não sabe sem execução mental qual cursor acessa itens e qual acessa produtos |

---

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express — LMS API)

Arquivos originais: `src/app.js`, `src/AppManager.js`, `src/utils.js` (~180 linhas totais)

| # | Severidade | Arquivo / Linhas | Problema | Por que é relevante |
|---|-----------|-----------------|----------|---------------------|
| 1 | **CRITICAL** | `src/AppManager.js:1–141` | **God Class**: `AppManager` acumula 6+ responsabilidades: inicialização do banco, seed, rotas HTTP, lógica de pagamento, gestão de usuários e logging de auditoria | Impossível testar qualquer camada de forma isolada sem subir banco e servidor HTTP completos |
| 2 | **CRITICAL** | `src/utils.js:1–7` | **Credenciais hardcoded**: senha de banco de produção (`"senha_super_secreta_prod_123"`) e chave live de gateway de pagamento (`"pk_live_1234567890abcdef"`) versionadas no git | Violação direta de PCI-DSS e LGPD; qualquer acesso ao repositório concede acesso pleno às credenciais de produção |
| 3 | **CRITICAL** | `src/utils.js:17–22` | **Hashing de senha não criptográfico**: `badCrypto()` concatena substrings de base64 em loop de 10.000 iterações — não é um algoritmo de hash real, é trivialmente reversível e nenhuma lib de hashing dedicada é usada | Senhas de usuários criados no checkout (`AppManager.js:66`) ficam protegidas por um "hash" caseiro sem nenhuma garantia criptográfica, equivalente a armazenar a senha quase em claro |
| 4 | **CRITICAL** | `src/AppManager.js:80,131` | **Rotas administrativas sem autenticação**: `/api/admin/financial-report` e `DELETE /api/users/:id` não verificam header `Authorization`, token ou papel de admin | Qualquer cliente não autenticado lê dados financeiros sensíveis (receita, alunos, valores pagos) ou apaga qualquer usuário apenas conhecendo o ID |
| 5 | **HIGH** | `src/AppManager.js:28–78` | **Fat Controller — Checkout**: handler HTTP de 50 linhas com validação, busca de curso, criação de usuário, aprovação de pagamento e log de auditoria aninhados em callbacks | Regra de negócio de pagamento (`cc.startsWith("4")`) não pode ser testada sem simular uma requisição HTTP completa |
| 6 | **HIGH** | `src/AppManager.js:80–129` | **Fat Controller — Relatório**: lógica de agregação financeira (receita por curso, lista de estudantes com valores pagos) embutida no handler HTTP com 49 linhas de callbacks aninhados | Impossível reutilizar a lógica de agregação em outro contexto (job assíncrono, exportação CSV) |
| 7 | **HIGH** | `src/utils.js:9–10` | **Global Mutable State**: `globalCache` e `totalRevenue` são variáveis mutáveis exportadas no escopo do módulo, compartilhadas entre todas as requisições | Em Node.js single-process, dados de um usuário ficam acessíveis para outros via o mesmo cache sem isolamento |
| 8 | **MEDIUM** | `src/AppManager.js:89–128` | **N+1 Query**: para N cursos com M matrículas cada, são executadas 1+N+(N×M×2) queries; com 10 cursos e 50 matrículas = ~1001 queries por request | Degrada linearmente com volume; tornando o endpoint de relatório financeiro inutilizável em produção |
| 9 | **MEDIUM** | `src/AppManager.js:29–35` | **Input sem validação**: validação apenas verifica presença de 4 campos sem validar tipo de `cid` (int), formato de email ou tamanho de `cc` | Criação silenciosa de usuários com senha vazia; campo de cartão aceita qualquer string |
| 10 | **LOW** | `src/AppManager.js:46` | **Magic String**: `cc.startsWith("4")` para identificar cartão Visa sem constante nomeada; `"PAID"` e `"DENIED"` repetidos sem enum | Regra de negócio de pagamento invisível; mudança de prefixo ou status exige busca manual |
| 11 | **LOW** | `src/AppManager.js:29–33` | **Poor Naming**: variáveis de letra única (`u`, `e`, `p`) e abreviações opacas (`cid`, `cc`) em escopo de função de 50 linhas; `processPaymentAndEnroll` viola SRP pelo próprio nome ("and" indica múltiplas responsabilidades) | Dificulta leitura e onboarding; um novo desenvolvedor não sabe o que cada variável representa sem rastrear seu uso pelo corpo inteiro da função |

---

### Projeto 3 — `task-manager-api` (Python/Flask — Task Manager)

Arquivos originais: `app.py`, `database.py`, `models/`, `routes/` (5 arquivos de rota), `services/`, `utils/` (~1161 linhas totais)

| # | Severidade | Arquivo / Linhas | Problema | Por que é relevante |
|---|-----------|-----------------|----------|---------------------|
| 1 | **CRITICAL** | `routes/task_routes.py:1–300` | **God Route File**: arquivo de 300 linhas com 5 responsabilidades distintas — roteamento HTTP, acesso direto ao ORM (`Task.query`), validação de entrada, lógica de negócio (cálculo de overdue) e serialização manual | Violação de SRP; impossível testar a lógica de overdue sem simular uma request HTTP |
| 2 | **CRITICAL** | `app.py:11–13` | **Credenciais hardcoded**: `SECRET_KEY = 'super-secret-key-123'` e `SQLALCHEMY_DATABASE_URI` literais no código-fonte | Exposição de chave de sessão no histórico git; se vazada, permite forjar qualquer sessão da aplicação |
| 3 | **CRITICAL** | `services/notification_service.py:7–10` | **Credenciais hardcoded**: `email_password = 'senha123'` e `email_user = 'taskmanager@gmail.com'` hardcoded no construtor do serviço | Credenciais SMTP de produção versionadas; qualquer acesso ao repositório permite usar a conta de email da aplicação |
| 4 | **CRITICAL** | `routes/user_routes.py:207–210` | **Token fake previsível**: `'fake-jwt-token-' + str(user.id)` como resposta de login | Token trivialmente forjável — qualquer cliente calcula o token de qualquer usuário apenas sabendo seu ID, sem nunca ter se autenticado de fato |
| 5 | **CRITICAL** | `models/user.py:27–32` | **Hashing de senha reversível/fraco**: `set_password`/`check_password` usam `hashlib.md5` sem salt, e o hash resultante ainda é incluído em `user.to_dict()` retornado pela API | Um vazamento do banco (ou a própria resposta da API, que já expõe o hash) compromete a senha na prática — MD5 é quebrado por rainbow tables e força bruta em GPU em minutos |
| 6 | **HIGH** | `routes/task_routes.py:12–63` | **Fat Route**: função `get_tasks()` de 51 linhas com cálculo de overdue, resolução de relacionamentos, serialização manual e condicionais aninhadas em 3 níveis — ignorando `Task.is_overdue()` e `Task.to_dict()` já existentes no model | Lógica de overdue duplicada em 6 pontos da codebase; mudança na definição exige editar 6 arquivos |
| 7 | **HIGH** | `routes/report_routes.py:12–101` | **Fat Route — Relatório**: função de 90 linhas calculando produtividade por usuário, contando overdue e agregando estatísticas dentro do handler HTTP | Impossível reutilizar ou testar a lógica de relatório sem simular uma request |
| 8 | **MEDIUM** | `routes/task_routes.py:41–57` | **N+1 Query**: para cada task, uma query busca `User` e outra busca `Category` — ignorando os relacionamentos ORM com `joinedload` disponíveis | Com 100 tasks = 201 queries por request; os relacionamentos já estão definidos no ORM e apenas precisam de eager loading |
| 9 | **MEDIUM** | `routes/task_routes.py`, `routes/user_routes.py`, `routes/report_routes.py` | **Código duplicado**: bloco de lógica de overdue copiado em 6 pontos; serialização manual de Task em 3 arquivos ignorando `Task.to_dict()` existente | Correção de bug em um ponto não propaga para os outros; campos diferem entre cópias, criando inconsistência silenciosa |
| 10 | **MEDIUM** | `routes/task_routes.py`, `routes/user_routes.py`, `routes/report_routes.py` | **API deprecated**: `Model.query.get(pk)` usado em 8 locais — deprecated no SQLAlchemy 2.x com `LegacyAPIWarning` em runtime | Bloqueia upgrade do Flask-SQLAlchemy; emite warnings em produção; será removido em versão futura |
| 11 | **LOW** | `routes/task_routes.py:96–114` | **Magic Numbers**: literais `3`, `200`, `1`, `5` e `4` (validações de comprimento de título, range de prioridade e tamanho mínimo de senha) hardcoded em `create_task` e `update_task`, apesar de `utils/helpers.py` já definir `MIN_TITLE_LENGTH`, `MAX_TITLE_LENGTH` e `MIN_PASSWORD_LENGTH` | Regra de negócio duplicada e invisível; as constantes corretas já existem no projeto mas são ignoradas pelas rotas, criando risco de valores divergentes entre validações |
| 12 | **LOW** | `routes/report_routes.py:24–28` | **Poor Naming**: variáveis `p1`, `p2`, `p3`, `p4`, `p5` para contagens de prioridade sem nome descritivo | Leitor não sabe que `p1` significa "contagem de tasks com prioridade crítica" sem ler todo o contexto circundante |

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
| `antipatterns-catalog.md` | 14 anti-patterns com IDs (AP-01…AP-14), sinais de detecção agnósticos e exemplos em 4 stacks |
| `template_audit_report.md` | Formato exato do relatório: cabeçalho, executive summary, bloco por finding (severidade, arquivo, linhas, trecho, problema, ação) |
| `architecture_guidelines.md` | Estrutura de diretórios MVC alvo, responsabilidades de cada camada, checklist pós-refatoração |
| `refactoring-playbook.md` | 13 padrões de transformação (PT-01…PT-13) com código ANTES/DEPOIS e ordem de aplicação recomendada |

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
| AP-13 | Weak / Reversible Password Hashing | CRITICAL | Adicionado após revisão dos 3 projetos: senhas protegidas com MD5/SHA sem salt (hash rápido, não projetado para senha); presente nos projetos 2 e 3 |
| AP-14 | Fake or Predictable Authentication Token | CRITICAL | Adicionado após revisão dos 3 projetos: login retorna token previsível (`'fake-jwt-token-' + id`, `f'placeholder-{id}'`) sem assinatura nem verificação nas rotas; presente nos 3 projetos |

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

**Desafio 5 — Vulnerabilidades de autenticação não cobertas pelo catálogo inicial**
Os 12 anti-patterns originais não capturavam dois problemas de segurança presentes nos 3 projetos: senhas hasheadas com algoritmo rápido sem salt (MD5/SHA puro) e tokens de login fake/previsíveis (`f'placeholder-{id}'`, `'fake-jwt-token-' + id`) aceitos sem qualquer verificação nas rotas. Solução: o catálogo foi estendido com `AP-13 — Weak / Reversible Password Hashing` e `AP-14 — Fake or Predictable Authentication Token` (ambos CRITICAL), e o `refactoring-playbook.md` ganhou os padrões correspondentes `PT-12` e `PT-13`. Os três relatórios de auditoria em `reports/` foram reexecutados/atualizados para incluir os novos findings.

---

## C) Resultados

### Resumo dos relatórios de auditoria

| Projeto | Stack | Arquivos analisados | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---------|-------|---------------------|----------|------|--------|-----|-------|
| `code-smells-project` | Python/Flask 3.1.1 | 4 (~781 linhas) | 8 | 5 | 6 | 4 | **23** |
| `ecommerce-api-legacy` | Node.js/Express 4.18.2 | 7 (~180 linhas) | 7 | 4 | 3 | 2 | **16** |
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
│   ├── usuario.py                   # senha protegida com bcrypt (hashpw/checkpw), nunca plaintext
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
│   ├── auth_routes.py               # /login emite JWT real (PyJWT) via usuario_controller
│   ├── auth_middleware.py           # decorator que valida o header Authorization nas rotas protegidas
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
│   ├── userModel.js                 # senha protegida com bcrypt.hash/compare, sem badCrypto
│   ├── courseModel.js
│   ├── enrollmentModel.js
│   ├── paymentModel.js
│   ├── auditModel.js
│   └── reportModel.js               # JOIN único substituindo N+1
├── controllers/
│   ├── checkoutController.js        # lógica de pagamento isolada
│   ├── reportController.js
│   ├── userController.js
│   ├── authController.js            # login emite JWT real via jsonwebtoken
│   └── constants.js                 # VISA_PREFIX, PAYMENT_STATUS enum
├── services/
│   └── tokenService.js              # geração/verificação do JWT (sign/verify)
├── middleware/
│   └── authMiddleware.js            # valida Authorization e protege /admin/financial-report e DELETE /users/:id
└── routes/
    ├── checkoutRoutes.js
    ├── reportRoutes.js
    ├── userRoutes.js
    ├── authRoutes.js
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
│                         # User.set_password/check_password migrados de md5 para werkzeug.security
├── controllers/          # nova camada — lógica extraída das rotas
│   ├── task_controller.py
│   ├── user_controller.py           # login emite JWT real (PyJWT) em vez de 'fake-jwt-token-<id>'
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
    ├── helpers.py        # constantes agora importadas e usadas nas rotas
    └── auth.py           # decorator que valida o JWT e protege as rotas exigidas
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
- [x] Mínimo de 5 findings identificados (23 encontrados)
- [x] Detecção de APIs deprecated incluída (não aplicável neste projeto)
- [x] Detecção de token fake incluída (AP-14: `/login` não emite token nem exige `Authorization` em nenhuma rota); hashing de senha não aplicável (senhas em plaintext, já coberto por AP-02b)
- [x] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para `.env.example` (sem hardcoded)
- [x] Models criados para abstrair dados com queries parametrizadas
- [x] Routes separadas por domínio para roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado nas rotas
- [x] Entry point limpo (`app.py` registra blueprints apenas)
- [x] Senha de usuário hasheada com `bcrypt` (`models/usuario.py`), plaintext removido do seed (AP-13 corrigido)
- [x] `/login` emite JWT assinado e expirável (`PyJWT`); `auth_middleware.py` valida `Authorization` nas rotas protegidas (AP-14 corrigido)
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
- [x] Mínimo de 5 findings identificados (16 encontrados)
- [x] Detecção de APIs deprecated incluída (não aplicável neste projeto)
- [x] Detecção de hashing fraco de senha e token fake incluída (AP-13: SHA-256 sem salt em `userModel.js` e no seed; AP-14: `financial-report` e `DELETE /users/:id` sem verificação de token)
- [x] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para `config.js` com `process.env` (sem hardcoded)
- [x] Models criados para abstrair acesso ao banco (6 models)
- [x] Routes separadas por domínio para roteamento HTTP
- [x] Controllers concentram a lógica de negócio
- [x] Error handling centralizado
- [x] Entry point limpo (`app.js` registra rotas apenas)
- [x] `badCrypto()` removido; senha hasheada com `bcrypt.hash`/`bcrypt.compare` em `userModel.js` (AP-13 corrigido)
- [x] `authController.js`/`tokenService.js` emitem JWT real (`jsonwebtoken`); `authMiddleware.js` protege `/admin/financial-report` e `DELETE /users/:id` (AP-14 corrigido)
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
- [x] Mínimo de 5 findings identificados (17 encontrados)
- [x] Detecção de APIs deprecated incluída (AP-12: `Model.query.get()` em 8 locais)
- [x] Detecção de hashing fraco de senha e token fake incluída (AP-13: `User.set_password`/`check_password` com MD5; AP-14: login retorna `f'placeholder-{user.id}'`)
- [x] Skill pausa e pede confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC (camada `controllers/` adicionada)
- [x] Configuração extraída para `config.py` com `os.environ.get()` (sem hardcoded)
- [x] Models mantidos e corretamente utilizados via `to_dict()` e `is_overdue()`
- [x] Routes enxutas (parse + validação + chamada ao controller)
- [x] Controllers concentram lógica de negócio extraída das rotas
- [x] Error handling centralizado com `controllers/exceptions.py`
- [x] Entry point limpo
- [x] `User.set_password`/`check_password` migrados de `hashlib.md5` para `werkzeug.security` (AP-13 corrigido)
- [x] Login emite JWT real (`pyjwt`) em vez de `'fake-jwt-token-' + id`; `utils/auth.py` valida o token nas rotas protegidas (AP-14 corrigido)
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

http://localhost:3000/api/login

```


<img width="1413" height="486" alt="login ecommerce-api" src="https://github.com/user-attachments/assets/66a4f036-5be9-46d9-a49f-1f63bd164d97" />


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

<img width="1411" height="405" alt="Acesso restrito" src="https://github.com/user-attachments/assets/6f12dc02-874e-4416-91e9-f46bf693873e" />

<img width="1420" height="653" alt="Acesso admin" src="https://github.com/user-attachments/assets/ac037c7e-1af7-46d7-b3b3-989db3ffa1a8" />


```

http://localhost:3000/api/users/2

```

<img width="1480" height="103" alt="Captura de tela de 2026-07-08 18-17-47" src="https://github.com/user-attachments/assets/7cdb5ab6-db5e-4100-87b5-7dc19c539392" />



<img width="1408" height="383" alt="deletando usuario" src="https://github.com/user-attachments/assets/f793f345-1679-4593-b7c9-33bfef754fd2" />



#### Projeto 3 — `task-manager-api`

```

http://localhost:5000/reports/summary

```

<img width="1079" height="570" alt="Login task-manager" src="https://github.com/user-attachments/assets/a020b039-88fd-4b62-864e-11bbc7d47726" />


```

http://localhost:5000/categories

```

<img width="1430" height="889" alt="Categorias" src="https://github.com/user-attachments/assets/d663342c-b468-49a4-9458-d4a531394069" />


```

http://localhost:5000/categories/create

```

<img width="1410" height="491" alt="image" src="https://github.com/user-attachments/assets/123791f0-b73a-48c2-a76b-f70e83d5608b" />


```

http://localhost:5000/health

```

<img width="1411" height="430" alt="health task-manager" src="https://github.com/user-attachments/assets/7e62e68d-675f-45d8-86a2-6c92b11d0c46" />

```

http://localhost:5000/reports/summary

```

<img width="1405" height="866" alt="summary" src="https://github.com/user-attachments/assets/72e7b855-bc83-43c5-9a2f-7b21590ef56a" />


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


### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.

---