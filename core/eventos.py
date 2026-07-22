from random import sample

from data.eventos import EVENTOS


def sortear_eventos(qtd: int = 3, evitar_ids: list[int] | None = None):
    """Sorteia eventos, priorizando cenários diferentes da tentativa anterior.

    Quando há eventos suficientes, nenhum evento da tentativa imediatamente anterior
    é repetido. Se o conjunto disponível for menor que a quantidade solicitada, a
    função completa a seleção com eventos anteriores, sem duplicar dentro da mesma
    tentativa.
    """
    qtd = min(max(0, qtd), len(EVENTOS))
    if qtd == 0:
        return []

    evitar = set(evitar_ids or [])
    novos = [evento for evento in EVENTOS if evento["id"] not in evitar]
    anteriores = [evento for evento in EVENTOS if evento["id"] in evitar]

    selecionados = sample(novos, min(qtd, len(novos)))
    faltantes = qtd - len(selecionados)
    if faltantes > 0:
        selecionados.extend(sample(anteriores, min(faltantes, len(anteriores))))
    return selecionados


def obter_evento(eventos, indice):
    if indice >= len(eventos):
        return None
    return eventos[indice]
