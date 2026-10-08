import argparse
import os
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from .auth import login
from .pdf import capturar_pagina_como_pdf, unir_pdfs
from .periods import gerar_periodos
from .turmas import buscar_turmas_do_periodo, ir_para_consulta_de_turmas
from .util import slugify

OUTPUT_DIR = Path("output")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Gera um PDF com as turmas ministradas por um docente no SIGAA UFCG, "
            "do período inicial até o período atual."
        )
    )
    parser.add_argument(
        "--docente",
        required=True,
        help='Nome do docente, ex. "João Arthur Brunet Monteiro"',
    )
    parser.add_argument(
        "--periodo-inicial",
        required=True,
        help="Período inicial no formato ano.semestre, ex. 2014.1",
    )
    parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Rodar o navegador sem interface (default) ou visível (--no-headless) para depuração",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    usuario = os.environ.get("SIGAA_USER")
    senha = os.environ.get("SIGAA_SENHA")
    if not usuario or not senha:
        sys.exit("SIGAA_USER e SIGAA_SENHA precisam estar definidos no .env")

    args = parse_args()
    periodos = gerar_periodos(args.periodo_inicial)

    OUTPUT_DIR.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        capturados = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=args.headless)
            page = browser.new_page()
            page.add_locator_handler(
                page.locator("#sigaa-cookie-consent"),
                lambda modal: modal.get_by_role("button", name="Ciente").click(),
            )

            login(page, usuario, senha)

            for periodo in periodos:
                ir_para_consulta_de_turmas(page)
                teve_resultado = buscar_turmas_do_periodo(page, args.docente, periodo)
                if not teve_resultado:
                    continue
                destino = tmp_dir / f"{periodo}.pdf"
                capturar_pagina_como_pdf(page, destino)
                capturados.append(destino)

            browser.close()

        if not capturados:
            sys.exit("Nenhuma turma encontrada em nenhum período pesquisado.")

        periodo_final = periodos[-1]
        nome_arquivo = (
            f"turmas_{slugify(args.docente)}_{args.periodo_inicial}_a_{periodo_final}.pdf"
        )
        destino_final = OUTPUT_DIR / nome_arquivo
        unir_pdfs(capturados, destino_final)

    print(f"PDF gerado em: {destino_final}")
