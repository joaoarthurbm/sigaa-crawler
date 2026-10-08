# SIGAA Crawler

Automação em Python que acessa o SIGAA da UFCG de forma programática (via navegador headless, não navegação manual) para reunir em PDF as evidências de atividades de um docente exigidas por uma comissão: turmas ministradas, orientações de iniciação científica e, no futuro, outras.

## Language

### Sistema

**SIGAA**:
Sistema Integrado de Gestão de Atividades Acadêmicas, usado pela UFCG (`sigaa.ufcg.edu.br`).

**Portal do Docente**:
Área autenticada do SIGAA onde um professor acessa turmas, consultas e documentos. É o único perfil de acesso usado por este crawler.

**Funcionalidade**:
Um tipo de evidência que o crawler sabe produzir (ex.: turmas, orientações de IC). Cada funcionalidade gera seu próprio PDF.

### Tempo

**Período**:
Semestre letivo da UFCG, identificado como `ano.número` (ex.: `2026.1`). O número não indica a época do ano e o ano não é o ano civil: 2020.1 ocorreu em 2021, e existe um período 2020.3 anterior a ele. As datas reais de cada período estão em `calendario_ufcg.csv`.
_Avoid_: semestre, ano-período (quando se referir às datas reais).

### Evidências

**Relatório de Turmas**:
Tela emitida pelo SIGAA na Consulta de Turmas (Ensino → Consulta → Turmas, opção "formato de relatório") com as turmas de um docente num período e o número de matriculados. O SIGAA não gera PDF dela; o crawler captura a tela fiel.
_Avoid_: Declaração de Disciplinas Ministradas (é outro documento do SIGAA, não usado aqui), declaração de turmas.

**Declaração de Orientação**:
Documento oficial em PDF emitido pela Pró-Reitoria de Pós-Graduação e Pesquisa via SIGAA (Pesquisa → Declarações → Declaração de Orientações), um por projeto de pesquisa, listando os bolsistas de iniciação científica orientados e o período de cada um. Cada emissão gera um número de documento e um código de verificação novos.
_Avoid_: certificado, declaração de projeto (a "Declaração de Membro de Projeto" é outro documento).

**Orientação de IC**:
O vínculo entre o docente e um bolsista de iniciação científica num projeto, com modalidade (ex.: PIBIC/CNPq, PIBIC/UFCG) e um intervalo de datas próprio, que não coincide com o período do projeto.
_Avoid_: projeto (um projeto pode ter várias orientações).

**Crawler**:
O programa deste repositório que faz login no SIGAA e navega via navegador headless (Playwright), sem intervenção manual.
