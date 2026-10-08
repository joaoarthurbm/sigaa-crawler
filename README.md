# sigaa-crawler

Crawler para ajudar na coleta de declarações/comprovações para progressão da UFCG.

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

## Funcionalidades

Com o ambiente virtual ativado (`source .venv/bin/activate`):

### PDF com todas as turmas ministradas

```bash
python -m sigaa_crawler --docente "João Arthur Brunet Monteiro" --periodo-inicial 2014.1 
```

### Argumentos

| Argumento | Obrigatório | Descrição |
|---|---|---|
| `--docente` | sim | Nome do docente como aparece no SIGAA (use aspas). |
| `--periodo-inicial` | sim | Primeiro período a buscar, no formato `ano.semestre` (ex. `2014.1`). A busca vai até o período atual. |
| `--no-headless` | não | Abre o navegador visível, para acompanhar a navegação. Por padrão o navegador roda oculto. |

O pdf gerado estará ./output. Exemplo:

```
output/turmas_joao_arthur_brunet_monteiro_2014.1_a_2026.2.pdf
```

### Erros comuns

- **`SIGAA_USER e SIGAA_SENHA precisam estar definidos no .env`**: o arquivo
  `.env` não existe ou está incompleto. Rode o comando a partir da raiz do
  repositório.
- **`Login falhou`**: usuário ou senha incorretos (a senha diferencia
  maiúsculas de minúsculas).
- **Timeout esperando um link ou campo**: o rótulo na tela real é diferente
  do esperado em `sigaa_crawler/turmas.py`; ajuste o seletor correspondente.
- **`Nenhuma turma encontrada`**: nenhum período retornou resultado; confira
  se o nome do docente está escrito exatamente como no SIGAA.
