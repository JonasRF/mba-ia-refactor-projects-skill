## 2. Formato do Relatório

Imprima o relatório seguindo exatamente esta estrutura, substituindo os campos `< >` pelos
valores encontrados na auditoria.

================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do diretório raiz>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<M> lines of code
Date:    <YYYY-MM-DD>

EXECUTIVE SUMMARY
-----------------
Total findings : <N>
  CRITICAL     : <N>
  HIGH         : <N>
  MEDIUM       : <N>
  LOW          : <N>

================================================================
FINDINGS
================================================================

[CRITICAL] <AP-ID> — <Nome do Anti-Pattern>
File    : <caminho/arquivo.py>
Lines   : <N>–<N>
---
<trecho de código — máximo 10 linhas>
---
Problem : <explicação objetiva de por que é um problema>
Action  : <ação de refatoração recomendada>

----------------------------------------------------------------

[HIGH] <AP-ID> — <Nome do Anti-Pattern>
File    : <caminho/arquivo.py>
Lines   : <N>–<N>
---
<trecho de código — máximo 10 linhas>
---
Problem : <explicação objetiva de por que é um problema>
Action  : <ação de refatoração recomendada>

----------------------------------------------------------------

[MEDIUM] <AP-ID> — <Nome do Anti-Pattern>
File    : <caminho/arquivo.py>
Lines   : <N>–<N>
---
<trecho de código — máximo 10 linhas>
---
Problem : <explicação objetiva de por que é um problema>
Action  : <ação de refatoração recomendada>

----------------------------------------------------------------

[LOW] <AP-ID> — <Nome do Anti-Pattern>
File    : <caminho/arquivo.py>
Lines   : <N>–<N>
---
<trecho de código — máximo 10 linhas>
---
Problem : <explicação objetiva de por que é um problema>
Action  : <ação de refatoração recomendada>


================================================================
Findings : <N total> 
================================================================
