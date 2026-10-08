import re
from datetime import date, datetime
from pathlib import Path

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pypdf import PdfReader

PORTAL_DOCENTE_URL = "https://sigaa.ufcg.edu.br/sigaa/portais/docente/docente.jsf"

# Linha de bolsista na declaração, ex. "PIBIC/UFCG (IC) 16/09/2024 a 31/08/2025".
# A data final pode faltar em orientações em andamento ("até a presente data").
_INTERVALO = re.compile(
    r"(\d{2}/\d{2}/\d{4})\s*(?:a|até)\s*(\d{2}/\d{2}/\d{4}|a presente data)"
)


def ir_para_declaracoes_de_orientacao(page: Page) -> None:
    # Abrir a URL da lista direto mostra "Projetos Encontrados (0)": o SIGAA só
    # carrega a lista quando se chega pelo menu. O item fica num dropdown
    # oculto, mas o clique só dispara um submit JSF, então basta o evento.
    page.goto(PORTAL_DOCENTE_URL)
    page.locator('[id="menu:declaracaoOrientacoes"]').dispatch_event("click")
    page.wait_for_load_state("networkidle")


def baixar_declaracoes(page: Page, destino_dir: Path) -> list[Path]:
    links = page.locator('a[title^="Emitir Declara"]')
    try:
        links.first.wait_for(timeout=10_000)
    except PlaywrightTimeoutError:
        return []

    arquivos = []
    for i in range(links.count()):
        with page.expect_download() as download:
            links.nth(i).click()
        destino = destino_dir / f"declaracao_orientacao_{i}.pdf"
        download.value.save_as(destino)
        arquivos.append(destino)
    return arquivos


def _data(texto: str, hoje: date) -> date:
    if texto == "a presente data":
        return hoje
    return datetime.strptime(texto, "%d/%m/%Y").date()


def intervalos_dos_bolsistas(arquivo: Path, hoje: date) -> list[tuple[date, date]]:
    texto = "\n".join(p.extract_text() for p in PdfReader(arquivo).pages)
    return [(_data(ini, hoje), _data(fim, hoje)) for ini, fim in _INTERVALO.findall(texto)]


def sobrepoe(intervalos: list[tuple[date, date]], inicio: date, fim: date) -> bool:
    return any(ini <= fim and fim_bolsa >= inicio for ini, fim_bolsa in intervalos)
