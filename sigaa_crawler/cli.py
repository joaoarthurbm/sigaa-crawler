import argparse
import os
import sys
import tempfile
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Iterator

from dotenv import load_dotenv
from playwright.sync_api import Page, sync_playwright

from . import calendario
from .auth import login
from .orientacoes import (
    baixar_declaracoes,
    intervalos_dos_bolsistas,
    ir_para_declaracoes_de_orientacao,
    sobrepoe,
)
from .pdf import capturar_pagina_como_pdf, unir_pdfs
from .periods import gerar_periodos
from .turmas import buscar_turmas_do_periodo, ir_para_consulta_de_turmas
from .util import slugify

OUTPUT_DIR = Path("output")


def parse_args() -> argparse.Namespace:
    comum = argparse.ArgumentParser(add_help=False)
    comum.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Rodar o navegador sem interface (default) ou visível (--no-headless) para depuração",
    )

    parser = argparse.ArgumentParser(
        description="Gera PDFs com evidências de atividades docentes a partir do SIGAA UFCG."
    )
    sub = parser.add_subparsers(dest="funcionalidade", required=True)

    turmas = sub.add_parser(
        "turmas",
        parents=[comum],
        help="Relatórios de Turmas do período inicial até o período atual.",
    )
    turmas.add_argument(
        "--docente",
        required=True,
        help='Nome do docente, ex. "João Arthur Brunet Monteiro"',
    )
    turmas.add_argument(
        "--periodo-inicial",
        required=True,
        help="Período inicial no formato ano.semestre, ex. 2014.1",
    )

    orientacoes = sub.add_parser(
        "orientacoes-pibic",
        parents=[comum],
        help="Declarações de Orientação de IC com bolsistas ativos do período inicial até hoje.",
    )
    orientacoes.add_argument(
        "--periodo-inicial",
        required=True,
        help="Período inicial, que precisa estar em calendario_ufcg.csv, ex. 2017.2",
    )

    return parser.parse_args()


@contextmanager
def sessao_sigaa(headless: bool) -> Iterator[Page]:
    load_dotenv()
    usuario = os.environ.get("SIGAA_USER")
    senha = os.environ.get("SIGAA_SENHA")
    if not usuario or not senha:
        sys.exit("SIGAA_USER e SIGAA_SENHA precisam estar definidos no .env")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.add_locator_handler(
            page.locator("#sigaa-cookie-consent"),
            lambda modal: modal.get_by_role("button", name="Ciente").click(),
        )
        login(page, usuario, senha)
        try:
            yield page
        finally:
            browser.close()


def gerar_turmas(args: argparse.Namespace, tmp_dir: Path) -> Path:
    periodos = gerar_periodos(args.periodo_inicial)
    capturados = []

    with sessao_sigaa(args.headless) as page:
        for periodo in periodos:
            ir_para_consulta_de_turmas(page)
            if not buscar_turmas_do_periodo(page, args.docente, periodo):
                continue
            destino = tmp_dir / f"{periodo}.pdf"
            capturar_pagina_como_pdf(page, destino)
            capturados.append(destino)

    if not capturados:
        sys.exit("Nenhuma turma encontrada em nenhum período pesquisado.")

    destino_final = OUTPUT_DIR / (
        f"turmas_{slugify(args.docente)}_{args.periodo_inicial}_a_{periodos[-1]}.pdf"
    )
    unir_pdfs(capturados, destino_final)
    return destino_final


def gerar_orientacoes_pibic(args: argparse.Namespace, tmp_dir: Path) -> Path:
    cal = calendario.carregar_calendario()
    hoje = date.today()
    try:
        inicio = calendario.inicio_do_periodo(cal, args.periodo_inicial)
    except ValueError as erro:
        sys.exit(str(erro))

    with sessao_sigaa(args.headless) as page:
        ir_para_declaracoes_de_orientacao(page)
        declaracoes = baixar_declaracoes(page, tmp_dir)

    selecionadas = []
    for arquivo in declaracoes:
        intervalos = intervalos_dos_bolsistas(arquivo, hoje)
        if not intervalos:
            print(
                f"Aviso: nenhuma data de bolsista encontrada em {arquivo.name}; "
                "incluída para revisão manual.",
                file=sys.stderr,
            )
            selecionadas.append((date.min, arquivo))
        elif sobrepoe(intervalos, inicio, hoje):
            selecionadas.append((min(ini for ini, _ in intervalos), arquivo))

    if not selecionadas:
        sys.exit(f"Nenhuma orientação com bolsista ativo entre {inicio:%d/%m/%Y} e hoje.")

    selecionadas.sort()
    destino_final = OUTPUT_DIR / (
        f"orientacoes_pibic_{args.periodo_inicial}_a_{calendario.periodo_atual(cal, hoje)}.pdf"
    )
    unir_pdfs([arquivo for _, arquivo in selecionadas], destino_final)
    print(f"{len(selecionadas)} de {len(declaracoes)} declarações incluídas.")
    return destino_final


def main() -> None:
    args = parse_args()
    geradores = {
        "turmas": gerar_turmas,
        "orientacoes-pibic": gerar_orientacoes_pibic,
    }

    OUTPUT_DIR.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        destino_final = geradores[args.funcionalidade](args, Path(tmp))

    print(f"PDF gerado em: {destino_final}")
