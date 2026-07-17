# Skill: refactor-arch

Você é um especialista em arquitetura de software. Sua missão é analisar, auditar e refatorar
projetos legados para o padrão MVC, independente da linguagem ou framework utilizado.

Esta skill executa **3 fases sequenciais**. Execute **apenas a fase indicada abaixo** e aguarde
instrução antes de avançar para a próxima.

---

## FASE 1 — PROJECT ANALYSIS

**Objetivo:** Detectar a stack tecnológica do projeto atual e imprimir um resumo estruturado no
terminal. Nenhum arquivo deve ser criado ou modificado nesta fase.

### Instruções de execução

1. Leia o arquivo de referência `.claude/skills/refactor-arch/project-analysis.md`. Ele contém
   todas as heurísticas que você deve seguir para detectar linguagem, framework, banco de dados,
   arquitetura e domínio de negócio.

2. Aplique as heurísticas na seguinte ordem sobre os arquivos do **diretório atual**:
   - Seção 1: detectar a linguagem
   - Seção 2: detectar o framework e sua versão
   - Seção 3: listar as dependências relevantes
   - Seção 4: identificar banco de dados, tipo de acesso e tabelas/coleções
   - Seção 5: mapear a arquitetura atual e classificá-la
   - Seção 5.4: inferir o domínio de negócio

3. Leia todos os arquivos-fonte do projeto para coletar evidências concretas antes de preencher
   o resumo. Não assuma nada sem verificar no código.

4. Ao final, imprima **exatamente** o bloco abaixo no terminal, substituindo os campos `<>` pelos
   valores detectados, seguindo as regras de preenchimento da Seção 6 do arquivo de referência:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework> <versão>
Dependencies:  <dependências relevantes separadas por vírgula>
Domain:        <domínio> (<entidades principais separadas por vírgula>)
Architecture:  <classificação> — <descrição curta>
Source files:  <N> files analyzed
DB tables:     <tabelas ou coleções>
================================
```
Quando terminar, vá para a Fase 2 imediatamente — sem perguntar.
---

## FASE 2 — AUDIT

**Objetivo:** Cruzar todos os arquivos-fonte do projeto contra o catálogo de anti-patterns,
gerar um relatório estruturado de auditoria e aguardar confirmação do usuário antes de avançar
para a Fase 3. Nenhum arquivo do projeto deve ser criado ou modificado nesta fase.

### Instruções de execução

1. Leia o arquivo de referência `.claude/skills/refactor-arch/antipatterns-catalog.md` por
   completo. Memorize todos os anti-patterns listados, seus IDs (AP-01, AP-02, …) e sinais de
   detecção. O catálogo é a única fonte de verdade — não invente anti-patterns fora dele.

2. Leia o arquivo de referência `.claude/skills/refactor-arch/template_audit_report.md` por
   completo. Ele define o formato exato do relatório, as regras de preenchimento de cada campo
   e o tamanho máximo do trecho de código (10 linhas).

3. Leia **todos** os arquivos-fonte do projeto (excluindo `node_modules`, `.venv`, `venv`,
   `__pycache__`, `.git`, `dist`, `build`, `reports`, `.claude`).

4. Para **cada anti-pattern do catálogo**, na ordem em que aparecem no arquivo, execute os
   seguintes passos:
   a. Aplique todos os seus sinais de detecção sobre cada arquivo-fonte lido no passo 3.
   b. Se encontrar ao menos uma ocorrência: registre internamente como finding com
      (severidade, ID, arquivo, linhas, trecho de código, problema, ação).
   c. Se o mesmo anti-pattern ocorrer em múltiplos arquivos ou funções distintas com impactos
      diferentes, registre um finding separado para cada ocorrência relevante.
   d. Se não encontrar nenhuma ocorrência: não registre finding e siga para o próximo.

5. Após varrer **todos** os anti-patterns do catálogo, compile a lista final de findings.
   Conte os findings por severidade: CRITICAL, HIGH, MEDIUM, LOW. Esses números são os que
   vão para o Executive Summary — preencha o Summary **somente depois** de ter a lista completa.

6. Imprima o relatório no terminal e salve em `reports/audit-project-<N>.md`, onde `<N>` é o
   próximo número sequencial disponível na pasta. Siga **exatamente** o formato do
   `template_audit_report.md`: findings ordenados de CRITICAL → HIGH → MEDIUM → LOW; dentro
   de cada nível, na ordem em que os anti-patterns aparecem no catálogo.

7. Ao final do relatório impresso, exiba:
   `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`
   Aguarde a resposta humana. Se não vier ou for `n`, encerre.

---

## FASE 3 — REFATORAÇÃO

**Objetivo:** Transformar o código-fonte do projeto para o padrão MVC definido nos arquivos de
referência, corrigindo todos os anti-patterns identificados na Fase 2. Ao final, validar que
a aplicação inicializa sem erros e que todos os endpoints originais respondem corretamente.

### Instruções de execução

1. Leia o arquivo `.claude/skills/refactor-arch/architecture_guidelines.md` por completo. Ele
   define a estrutura de diretórios alvo, as responsabilidades de cada camada (Model, Controller,
   Routes/View, Database, Bootstrap) e o checklist de validação pós-refatoração. É a única fonte
   de verdade sobre **onde** cada trecho de código deve ficar. Os exemplos estão em Python/Flask,
   mas os princípios se aplicam à stack detectada na Fase 1 — adapte nomenclatura e convenções
   conforme a linguagem e o framework do projeto.

2. Leia o arquivo `.claude/skills/refactor-arch/refactoring-playbook.md` por completo. Ele define
   os padrões concretos de transformação (PT-01 a PT-13) com código ANTES/DEPOIS e os passos
   exatos de cada transformação — incluindo PT-12 (hash de senha seguro) e PT-13 (autenticação
   real com token assinado/expirável), que corrigem as causas raiz de senha em hash fraco e token
   fake/previsível. Aplique os padrões **na ordem recomendada** da seção "Ordem de Aplicação
   Recomendada" do Playbook, adaptando a sintaxe e os idiomas à stack do projeto sem alterar os
   princípios estruturais.

3. Para cada anti-pattern listado no relatório da Fase 2 (CRITICAL → HIGH → MEDIUM → LOW),
   aplique o padrão de transformação correspondente do Playbook. Não pule nenhum finding.
   a. **Todo finding CRITICAL é obrigatório e bloqueante.** Nenhum finding CRITICAL do relatório
      da Fase 2 pode permanecer sem correção ao final da Fase 3.
   b. Se um finding CRITICAL foi registrado na Fase 2 sob um AP-ID que não cobre a causa raiz real
      do problema (ex.: hash fraco de senha ou token previsível registrados sob AP-02 por
      aproximação), identifique a categoria de segurança correta e aplique o padrão do Playbook
      mais específico para ela — não considere o finding resolvido só porque o AP-ID original foi
      tratado.

4. Ao criar ou modificar arquivos, garanta que a estrutura de diretórios final respeita o
   padrão MVC do `architecture_guidelines.md`, adaptado à convenção da stack detectada:
   - **Entry point** — arquivo de bootstrap que inicializa a aplicação, registra rotas e
     carrega configuração; não contém rotas nem lógica de negócio
   - **Config** — módulo de configuração que lê variáveis de ambiente; zero valores
     hardcoded no código-fonte
   - **Models** — camada de acesso a dados; queries parametrizadas, serialização centralizada;
     sem lógica de negócio
   - **Controllers** — lógica de negócio e orquestração; sem conhecimento do protocolo HTTP
   - **Routes/Views** — roteamento HTTP, parse de request, validação de presença e tipo de
     campos, mapeamento de erros para status codes; sem acesso direto ao banco
   - **Database** — gerenciamento do ciclo de vida da conexão, escopado por request
   - **Services** — side-effects externos (notificações, filas, e-mail), se houver

5. Após aplicar todas as transformações, execute mentalmente o checklist do
   `architecture_guidelines.md`. Verifique cada item contra os arquivos produzidos. Se algum
   item não estiver satisfeito, corrija antes de avançar para a validação.

6. **Gate de findings CRITICAL:** releia a lista de findings CRITICAL registrados no relatório da
   Fase 2. Para cada um, confirme nos arquivos finais que o sinal de detecção original do
   anti-pattern (a heurística/regex do `antipatterns-catalog.md`) não ocorre mais — por exemplo,
   busque por `hashlib.md5`, `hashlib.sha1`, tokens construídos por f-string/concatenação com ID,
   segredos literais, concatenação de SQL. Monte a contagem `<N resolvidos>/<N total>` de findings
   CRITICAL. Se qualquer um ainda estiver presente, a Fase 3 **não está completa**: volte ao passo
   3, aplique o padrão do Playbook faltante e repita este gate. Não prossiga para a validação de
   boot enquanto houver CRITICAL não resolvido.

7. **Validação de boot:** determine o comando de inicialização correto para a stack detectada
   na Fase 1 (ex: `node index.js`, `python app.py`, `go run main.go`, `mvn spring-boot:run`,
   `rails server`) e execute-o. Capture e exiba as primeiras linhas do output. Se a aplicação
   não subir, corrija o erro e repita até inicializar sem exceções ou erros fatais.

8. **Validação de endpoints:** com a aplicação rodando, teste cada endpoint mapeado na Fase 1
   usando a ferramenta de HTTP disponível no ambiente (`curl`, `httpie`, cliente nativo ou
   equivalente). Para cada chamada, exiba: comando executado, status HTTP retornado e trecho
   da resposta. Critérios mínimos de aceitação por tipo de operação:
   - Health check ou rota raiz → `2xx`
   - Listagem de recursos → `200` com coleção de dados
   - Criação de recurso → `201` com identificador gerado
   - Busca por identificador → `200` com objeto do recurso
   - Autenticação/login, se existir → `200` com token real (JWT/sessão assinada, nunca valor
     previsível) — valide também que uma rota protegida rejeita requests sem token ou com token
     inválido (`401`)
   - Criação de pedido/transação, se existir → `201` com registro criado

9. Ao final, imprima o bloco de conclusão abaixo no terminal, preenchendo os campos `<>`:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
Stack:               <linguagem> / <framework>
Patterns applied:    <IDs PT-XX aplicados, separados por vírgula>
Files created:       <N> novos arquivos
Files modified:      <N> arquivos modificados
Files removed:       <N> arquivos removidos

MVC Structure:       <OK | FAIL>
Config extracted:    <OK | FAIL> — variáveis de ambiente, zero hardcoded
Models layer:        <OK | FAIL> — queries parametrizadas, serialização centralizada
Routes layer:        <OK | FAIL> — roteamento isolado, sem lógica de negócio
Controllers layer:   <OK | FAIL> — regras de domínio isoladas, sem conhecimento HTTP
Error handling:      <OK | FAIL> — erros mapeados para status HTTP na camada Routes
Entry point:         <OK | FAIL> — bootstrap limpo, sem rotas nem lógica inline

Boot test:           <OK | FAIL — detalhe do erro>
Endpoints tested:    <N>/<total> passaram
CRITICAL findings:   <N resolvidos>/<N total> — 0 pendentes exigido
================================
```

Se `Boot test`, qualquer endpoint crítico, ou o gate de findings CRITICAL falhar, **não imprima o
bloco de conclusão** —
corrija o problema e repita os passos 6, 7 e 8 até todos os testes e o gate CRITICAL passarem.

