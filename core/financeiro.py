from typing import Dict, Tuple


def calcular_total_alocado(alocacoes: Dict[str, float]) -> float:
    return float(sum(alocacoes.values()))


def calcular_saldo_planejamento(
    alocacoes: Dict[str, float],
    orcamento_total: float,
) -> float:
    return float(orcamento_total) - calcular_total_alocado(alocacoes)


def analisar_riscos_alocacoes(
    alocacoes: Dict[str, float],
    orcamento_total: float,
) -> list[str]:
    """Identifica riscos financeiros sem bloquear a continuidade da simulação."""
    avisos: list[str] = []
    total = calcular_total_alocado(alocacoes)

    if total > orcamento_total:
        excesso = total - orcamento_total
        avisos.append(
            f"O planejamento ultrapassa os recursos disponíveis em R$ {excesso:,.2f}. "
            "A decisão será mantida para análise das consequências."
        )

    reserva = float(alocacoes.get("Reserva de contingência", 0.0))
    if reserva <= 0:
        avisos.append(
            "Não foi definida reserva de contingência. Isso aumenta a exposição "
            "a eventos inesperados."
        )
    elif orcamento_total > 0:
        percentual = (reserva / orcamento_total) * 100
        if percentual < 5:
            avisos.append(
                f"A reserva representa apenas {percentual:.1f}% dos recursos, "
                "abaixo da referência pedagógica de 5%."
            )

    return avisos


def validar_alocacoes(
    alocacoes: Dict[str, float],
    orcamento_total: float,
) -> Tuple[bool, str]:
    """Mantém compatibilidade com a interface, mas não bloqueia decisões gerenciais."""
    avisos = analisar_riscos_alocacoes(alocacoes, orcamento_total)
    if avisos:
        return True, "Decisão registrada com riscos financeiros identificados."
    return True, "Planejamento registrado sem riscos relevantes nesta etapa."


def analisar_riscos_escolhas_taticas(
    alocacoes: Dict[str, float],
    escolhas: Dict[str, Dict[str, float]],
) -> list[str]:
    """Compara escolhas e limites planejados sem impedir o avanço."""
    avisos: list[str] = []
    for categoria, escolha in escolhas.items():
        limite = float(alocacoes.get(categoria, 0.0))
        custo = float(escolha["custo"])

        if custo > limite:
            excesso = custo - limite
            avisos.append(
                f"{categoria}: a escolha custa R$ {custo:,.2f} e excede a "
                f"alocação em R$ {excesso:,.2f}."
            )

    return avisos


def validar_escolhas_taticas(
    alocacoes: Dict[str, float],
    escolhas: Dict[str, Dict[str, float]],
) -> Tuple[bool, str]:
    """Mantém compatibilidade, permitindo escolhas financeiramente inadequadas."""
    avisos = analisar_riscos_escolhas_taticas(alocacoes, escolhas)
    if avisos:
        return True, "Escolhas registradas com riscos de estouro das alocações."
    return True, "Escolhas táticas compatíveis com a distribuição estratégica."


def calcular_resumo_planejamento(
    alocacoes: Dict[str, float],
    escolhas: Dict[str, Dict[str, float]],
    orcamento_total: float,
) -> Dict[str, float]:
    custo_escolhas = sum(float(item["custo"]) for item in escolhas.values())
    reserva = float(alocacoes.get("Reserva de contingência", 0.0))
    saldo_nao_comprometido = orcamento_total - custo_escolhas - reserva

    return {
        "orcamento_total": float(orcamento_total),
        "total_alocado": calcular_total_alocado(alocacoes),
        "custo_escolhas": custo_escolhas,
        "reserva": reserva,
        "saldo_nao_comprometido": saldo_nao_comprometido,
        "percentual_reserva": (reserva / orcamento_total) * 100,
    }


def calcular_receita_inscricoes(
    quantidade_inscritos: int,
    valor_inscricao: float,
    capacidade: int,
) -> float:
    inscritos_validos = max(0, min(int(quantidade_inscritos), int(capacidade)))
    return inscritos_validos * float(valor_inscricao)


def calcular_receita_total(
    quantidade_inscritos: int,
    valor_inscricao: float,
    capacidade: int,
    patrocinio_base: float,
    patrocinio_extra: float = 0.0,
) -> Dict[str, float]:
    receita_inscricoes = calcular_receita_inscricoes(
        quantidade_inscritos,
        valor_inscricao,
        capacidade,
    )

    patrocinio_total = max(0.0, float(patrocinio_base)) + max(
        0.0,
        float(patrocinio_extra),
    )

    return {
        "receita_inscricoes": receita_inscricoes,
        "patrocinio_base": max(0.0, float(patrocinio_base)),
        "patrocinio_extra": max(0.0, float(patrocinio_extra)),
        "patrocinio_total": patrocinio_total,
        "receita_total": receita_inscricoes + patrocinio_total,
    }


def calcular_recursos_disponiveis(
    orcamento_inicial: float,
    receita_total: float,
) -> float:
    return float(orcamento_inicial) + float(receita_total)
