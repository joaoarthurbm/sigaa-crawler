# SIGAA Crawler

Automação em Python que acessa o SIGAA da UFCG de forma programática (via navegador headless, não navegação manual) para extrair dados acadêmicos do Portal do Docente, começando pelas turmas ministradas pelo professor João Arthur Brunet Monteiro.

## Language

**SIGAA**:
Sistema Integrado de Gestão de Atividades Acadêmicas, usado pela UFCG (`sigaa.ufcg.edu.br`). Aplicação JSF com sessão baseada em ViewState (estado por página embutido em campo oculto, não só cookies).

**Portal do Docente**:
Área autenticada do SIGAA onde um professor acessa suas turmas, consultas e documentos. É o perfil de acesso usado por este crawler (não Portal do Discente nem Portal do Coordenador).

**Consulta de Turmas**:
Tela em Portal do Docente → Ensino → Consulta → Turmas que permite pesquisar turmas por nome de docente. O resultado é renderizado na própria tela (não gera PDF pelo SIGAA); é a fonte de dados real usada pelo crawler.
_Avoid_: Declaração de Disciplinas Ministradas (hipótese inicial descartada — não é esse o caminho usado; a tela real é uma consulta/listagem, não um documento emitido pelo SIGAA).

**Declaração** (no contexto deste projeto):
Um PDF gerado a partir da captura fiel da tela de resultados da Consulta de Turmas (não um documento reformatado). O valor está em ser reconhecível como a tela real do SIGAA, para ser aceito como evidência por uma comissão.
_Avoid_: Relatório customizado, documento formatado (o crawler não deve gerar texto declaratório próprio).

**Período**:
Identificador de semestre acadêmico no formato ano.semestre (ex.: `2026.1`), usado para filtrar turmas por intervalo de tempo.

**Crawler**:
O script Python deste repositório que automatiza o login e a navegação no SIGAA via navegador headless (Playwright) com seletores fixos, sem intervenção manual do mouse.
