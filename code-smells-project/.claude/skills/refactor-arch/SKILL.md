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
DB Engine:     <banco de dados>
DB Access:     <ORM/ODM ou SQL direto>
DB tables:     <tabelas ou coleções>
================================
```

