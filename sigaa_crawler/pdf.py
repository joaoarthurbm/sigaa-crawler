from pathlib import Path

from playwright.sync_api import Page
from pypdf import PdfWriter


def capturar_pagina_como_pdf(page: Page, destino: Path) -> None:
    page.pdf(path=str(destino))


def unir_pdfs(arquivos: list[Path], destino: Path) -> None:
    writer = PdfWriter()
    for arquivo in arquivos:
        writer.append(str(arquivo))
    writer.write(str(destino))
    writer.close()
