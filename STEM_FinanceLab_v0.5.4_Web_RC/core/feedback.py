from __future__ import annotations

from typing import Any, Dict


def _valor_indicador(indicadores: Dict[str, Any], nome: str) -> float | None:
    for item in indicadores.get("linhas", []):
        if item.get("Indicador") == nome:
            resultado = item.get("Resultado")
            return None if resultado is None else float(resultado)
    return None


def gerar_feedback_aprendizagem(
    motor: Dict[str, Any],
    resumo: Dict[str, Any],
    dre: Dict[str, Any],
    indicadores: Dict[str, Any],
) -> Dict[str, list[str] | str]:
    """Transforma resultados já calculados em feedback pedagógico baseado em regras.

    Este módulo não realiza cálculos contábeis e não altera o resultado da simulação.
    Ele apenas interpreta informações produzidas pelo motor financeiro.
    """
    lucro = float(dre.get("lucro_liquido", 0.0))
    saldo = float(resumo.get("saldo_caixa", 0.0))
    reserva = float(resumo.get("reserva_planejada", 0.0))
    caixa_livre = float(resumo.get("caixa_livre_apos_reserva", 0.0))

    margem = _valor_indicador(indicadores, "Margem líquida")
    comprometimento = _valor_indicador(
        indicadores, "Comprometimento do orçamento inicial"
    )
    cobertura = _valor_indicador(
        indicadores, "Cobertura da reserva para imprevistos"
    )
    maior_gasto = _valor_indicador(indicadores, "Participação do maior gasto")
    dependencia = _valor_indicador(indicadores, "Dependência das inscrições")

    fatos: list[str] = []
    acertos: list[str] = []
    atencao: list[str] = []
    recomendacoes: list[str] = []
    reflexoes: list[str] = []

    if lucro >= 0:
        fatos.append("O projeto terminou com resultado econômico positivo.")
        acertos.append("As receitas foram suficientes para cobrir os gastos reconhecidos.")
    else:
        fatos.append("O projeto terminou com prejuízo econômico.")
        atencao.append("As receitas não foram suficientes para cobrir todos os gastos.")
        recomendacoes.append(
            "Revise os gastos de maior impacto e compare-os com a receita esperada antes de confirmar o planejamento."
        )

    if saldo >= 0:
        fatos.append("O Banco Conta Movimento encerrou com saldo não negativo.")
        acertos.append("O projeto conseguiu concluir a simulação sem saldo bancário final negativo.")
    else:
        fatos.append("O Banco Conta Movimento encerrou com saldo negativo.")
        atencao.append("Houve insuficiência de recursos financeiros ao final da execução.")
        recomendacoes.append(
            "Preserve maior margem de segurança entre os recursos disponíveis e os gastos contratados."
        )

    if reserva > 0 and caixa_livre >= 0:
        acertos.append("A reserva planejada pôde ser preservada no encerramento.")
    elif reserva > 0:
        atencao.append("O saldo final não foi suficiente para preservar integralmente a reserva planejada.")
        recomendacoes.append(
            "Reduza gastos discricionários ou aumente a reserva antes de assumir novas despesas."
        )

    if margem is not None:
        fatos.append(f"A margem líquida apurada foi de {margem:.2f}%.")

    if comprometimento is not None and comprometimento > 100:
        atencao.append(
            "Os gastos ultrapassaram o capital inicial e exigiram o uso das receitas do evento para sustentar a execução."
        )
    elif comprometimento is not None and comprometimento <= 90:
        acertos.append("O comprometimento do capital inicial permaneceu dentro de uma faixa de segurança.")

    if cobertura is not None and cobertura >= 100:
        acertos.append("A reserva planejada foi suficiente para absorver os gastos com imprevistos.")
    elif cobertura is not None and cobertura < 100:
        atencao.append("A reserva planejada não cobriu integralmente os gastos com imprevistos.")
        recomendacoes.append(
            "Reavalie o valor destinado à contingência considerando a exposição a eventos inesperados."
        )

    if maior_gasto is not None and maior_gasto >= 40:
        atencao.append("Uma única despesa concentrou parcela relevante dos gastos totais.")
        recomendacoes.append(
            "Negocie alternativas para o maior gasto e avalie fornecedores ou formatos equivalentes."
        )

    if dependencia is not None:
        fatos.append(f"As inscrições representaram {dependencia:.1f}% da receita bruta.")
        if dependencia >= 70:
            atencao.append("O projeto apresentou alta dependência da receita de inscrições.")
            recomendacoes.append(
                "Diversifique as fontes de receita por meio de patrocínios, parcerias ou apoios institucionais."
            )
        elif dependencia <= 50:
            acertos.append("A receita não ficou excessivamente concentrada nas inscrições.")

    contas_receber = float(resumo.get("contas_receber", 0.0))
    if contas_receber > 0:
        fatos.append("Parte da receita de inscrições permaneceu em Contas a Receber.")
        atencao.append(
            "Resultado econômico e disponibilidade bancária não são iguais quando existem valores ainda não recebidos."
        )

    reflexoes.extend(
        [
            "Qual decisão teve maior influência sobre o resultado final?",
            "Que gasto poderia ser reduzido sem comprometer a qualidade do evento?",
            "O que você faria de forma diferente em uma nova tentativa?",
        ]
    )

    if not acertos:
        acertos.append(
            "A tentativa produziu informações úteis para identificar escolhas que podem ser revistas."
        )
    if not atencao:
        atencao.append(
            "Mesmo com resultado favorável, compare as escolhas para identificar oportunidades de melhoria."
        )
    if not recomendacoes:
        recomendacoes.append(
            "Refaça a simulação alterando uma decisão por vez para observar seu efeito nos demonstrativos e indicadores."
        )

    return {
        "mensagem": (
            "Esta tentativa não possui caráter punitivo. Os erros fazem parte da experiência "
            "e podem orientar novas decisões nas próximas simulações."
        ),
        "fatos": fatos,
        "acertos": acertos,
        "atencao": atencao,
        "recomendacoes": recomendacoes,
        "reflexoes": reflexoes,
    }
