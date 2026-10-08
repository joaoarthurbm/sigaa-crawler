from playwright.sync_api import Page

BUSCA_TURMA_URL = "https://sigaa.ufcg.edu.br/sigaa/ensino/turma/busca_turma.jsf"


def _campo(page: Page, id_jsf: str):
    # IDs do JSF contêm ":", que precisaria de escape num seletor "#id".
    return page.locator(f'[id="{id_jsf}"]')


def ir_para_consulta_de_turmas(page: Page) -> None:
    page.goto(BUSCA_TURMA_URL)


def buscar_turmas_do_periodo(page: Page, docente: str, periodo: str) -> bool:
    ano, semestre = periodo.split(".")

    _campo(page, "form:checkDocente").check()
    _campo(page, "form:inputNomeDocente").fill(docente)

    _campo(page, "form:checkAnoPeriodo").check()
    _campo(page, "form:inputAno").fill(ano)
    _campo(page, "form:inputPeriodo").fill(semestre)

    _campo(page, "form:checkRel").check()

    _campo(page, "form:buttonBuscar").click()
    page.wait_for_load_state("networkidle")

    # Sem turmas, o SIGAA volta ao formulário com "Nenhuma turma encontrada...";
    # checar o título do relatório também evita capturar outras mensagens de erro.
    return page.get_by_text("Relatório de Turmas", exact=True).count() > 0
