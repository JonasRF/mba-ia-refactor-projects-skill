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

