import csv
from datetime import date, datetime
from pathlib import Path

CALENDARIO_CSV = Path(__file__).resolve().parent.parent / "calendario_ufcg.csv"


def _data(texto: str) -> date:
    return datetime.strptime(texto, "%d/%m/%Y").date()


def carregar_calendario() -> dict[str, tuple[date, date]]:
    with open(CALENDARIO_CSV, encoding="utf-8") as f:
        return {
            linha["periodo"]: (_data(linha["inicio"]), _data(linha["fim"]))
            for linha in csv.DictReader(f)
        }


def inicio_do_periodo(calendario: dict[str, tuple[date, date]], periodo: str) -> date:
    if periodo not in calendario:
        disponiveis = ", ".join(sorted(calendario, key=lambda p: calendario[p][0]))
        raise ValueError(
            f"Período {periodo} não está em {CALENDARIO_CSV.name}. Disponíveis: {disponiveis}"
        )
    return calendario[periodo][0]


def periodo_atual(calendario: dict[str, tuple[date, date]], hoje: date) -> str:
    # O número do período não segue o ano civil (2020.3 vem antes de 2020.1),
    # então o atual é o último a ter começado, pela data.
    iniciados = [p for p, (inicio, _) in calendario.items() if inicio <= hoje]
    return max(iniciados, key=lambda p: calendario[p][0])
