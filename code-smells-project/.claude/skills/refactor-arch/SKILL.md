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

1. Leia o arquivo de referência `.claude/skills/refactor-arch/antipatterns-catalog.md`. Ele
   contém os anti-patterns, sinais de detecção, exemplos de código e critérios de severidade
   que devem ser aplicados.

2. Leia o arquivo de referência `.claude/skills/refactor-arch/template_audit_report.md`. Ele
   define o formato exato do relatório a ser impresso, as regras de preenchimento de cada campo
   e o bloco de confirmação que deve ser exibido ao final.

3. Escaneie todos os arquivos-fonte do projeto aplicando os sinais de detecção de cada
   anti-pattern. Siga as regras de escopo da Seção 4 do `template_audit_report.md` (arquivos a
   ignorar, ordem dos findings, tamanho do trecho de código).

5. Imprima o relatório completo no terminal seguindo **exatamente** o formato da Seção 2 do
   `template_audit_report.md` e salve o relatório dentro da pasta reports com o seguinte nome audit-project-<N>.md.

6. Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]. Espere a resposta humana. Se ela não vier ou for negativa[n], encerre.

