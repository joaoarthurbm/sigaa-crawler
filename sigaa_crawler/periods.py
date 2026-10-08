from datetime import date


def _periodo_atual() -> str:
    hoje = date.today()
    semestre = 1 if hoje.month <= 6 else 2
    return f"{hoje.year}.{semestre}"


def _parse(periodo: str) -> tuple[int, int]:
    ano, semestre = periodo.split(".")
    return int(ano), int(semestre)


def gerar_periodos(periodo_inicial: str) -> list[str]:
    ano, semestre = _parse(periodo_inicial)
    ano_atual, semestre_atual = _parse(_periodo_atual())

    periodos = []
    while (ano, semestre) <= (ano_atual, semestre_atual):
        periodos.append(f"{ano}.{semestre}")
        if semestre == 1:
            semestre = 2
        else:
            semestre = 1
            ano += 1
    return periodos
