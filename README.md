# sigaa-crawler

Gera PDFs com evidências de atividades docentes a partir do SIGAA UFCG, sem
navegação manual. Cada funcionalidade é um subcomando:

- `turmas`: Relatórios de Turmas (Ensino → Consulta → Turmas) do período
  inicial até o período atual, capturando a tela real do SIGAA.
- `orientacoes-pibic`: Declarações de Orientação de iniciação científica
  (Pesquisa → Declarações → Declaração de Orientações) com algum bolsista
  ativo entre o início do período inicial e hoje.

Veja [CONTEXT.md](./CONTEXT.md) para o glossário do domínio e as decisões
já descartadas durante o design.

## Pré-requisitos

- Python 3.9 ou superior
- Login e senha do SIGAA UFCG com acesso ao Portal do Docente

## Instalação

Execute uma única vez, a partir da raiz do repositório:

```bash
# 1. Crie e ative um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instale as dependências Python
pip install -r requirements.txt

# 3. Baixe o navegador usado pelo Playwright
playwright install chromium

# 4. Configure suas credenciais
cp .env.example .env
```

Edite o `.env` com seu usuário e senha do SIGAA:

```
SIGAA_USER=seu_usuario
SIGAA_SENHA=sua_senha
```

O `.env` está no `.gitignore` e nunca deve ser commitado.

## Execução

Com o ambiente virtual ativado (`source .venv/bin/activate`), escolha o
subcomando. Todos aceitam `--no-headless`, que abre o navegador visível para
acompanhar a navegação; por padrão ele roda oculto.

Cada funcionalidade gera um único PDF em `./output/`.

### Turmas

```bash
python -m sigaa_crawler turmas --docente "João Arthur Brunet Monteiro" --periodo-inicial 2014.1
```

| Argumento | Obrigatório | Descrição |
|---|---|---|
| `--docente` | sim | Nome do docente como aparece no SIGAA (use aspas). |
| `--periodo-inicial` | sim | Primeiro período a buscar, no formato `ano.semestre` (ex. `2014.1`). A busca vai até o período atual. |

Gera uma página por período com turmas (períodos sem turma são pulados):

```
output/turmas_joao_arthur_brunet_monteiro_2014.1_a_2026.2.pdf
```

### Orientações PIBIC

```bash
python -m sigaa_crawler orientacoes-pibic --periodo-inicial 2017.2
```

| Argumento | Obrigatório | Descrição |
|---|---|---|
| `--periodo-inicial` | sim | Período a partir do qual as orientações contam. Precisa estar em `calendario_ufcg.csv`. |

Emite no SIGAA a Declaração de Orientação de cada projeto listado e mantém
as que têm pelo menos um bolsista com algum dia entre o início do período
inicial e hoje (o bolsista não precisa estar inteiro dentro do intervalo).
Entram todas as modalidades de iniciação científica. As declarações que
entram são unidas em ordem cronológica:

```
output/orientacoes_pibic_2017.2_a_2026.2.pdf
```

Cada execução emite declarações novas no SIGAA, cada uma com seu próprio
número de documento e código de verificação, como acontece ao clicar em
"Emitir Declaração" manualmente.

### Calendário acadêmico

`calendario_ufcg.csv` guarda as datas de início e fim de cada período da
UFCG. Os períodos não seguem o ano civil (2020.1 ocorreu em 2021, e 2020.3
veio antes dele), por isso as datas vêm do calendário e não do número do
período. Acrescente uma linha a cada novo período.

### Erros comuns

- **`SIGAA_USER e SIGAA_SENHA precisam estar definidos no .env`**: o arquivo
  `.env` não existe ou está incompleto. Rode o comando a partir da raiz do
  repositório.
- **`Login falhou`**: usuário ou senha incorretos (a senha diferencia
  maiúsculas de minúsculas).
- **Timeout esperando um link ou campo**: o SIGAA mudou a tela; rode com
  `--no-headless` para ver onde parou e ajuste o seletor em
  `sigaa_crawler/turmas.py` ou `sigaa_crawler/orientacoes.py`.
- **`Nenhuma turma encontrada`**: nenhum período retornou resultado; confira
  se o nome do docente está escrito exatamente como no SIGAA.
- **`Período X não está em calendario_ufcg.csv`**: acrescente as datas desse
  período ao calendário ou use um período que já esteja nele.
