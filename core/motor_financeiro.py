from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Iterable


def _agora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _moeda_br(valor: float) -> str:
    texto = f"{float(valor):,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _percentual_br(valor: float, casas: int = 1) -> str:
    return f"{float(valor):.{casas}f}".replace(".", ",") + "%"


def criar_motor_financeiro(
    orcamento_inicial: float,
    receita_inscricoes: float,
    patrocinio: float,
) -> Dict[str, Any]:
    """Cria um estado financeiro serializável para uso no Streamlit."""
    motor: Dict[str, Any] = {
        "versao": "1.1",
        "percentual_inscricoes_recebidas": 0.80,
        "orcamento_inicial": float(orcamento_inicial),
        "receita_inscricoes": float(receita_inscricoes),
        "patrocinio": float(patrocinio),
        "lancamentos": [],
    }

    # O capital inicial é um aporte patrimonial depositado no banco, não receita.
    registrar_lancamento(
        motor,
        fase="Financiamento",
        categoria="Capital inicial",
        descricao="Aporte inicial depositado no Banco Conta Movimento",
        tipo="entrada_banco",
        valor=orcamento_inicial,
        natureza_dre="nao_operacional",
        origem="cenario",
    )

    # As inscrições são reconhecidas pelo regime de competência. Nesta versão
    # pedagógica, 80% são recebidas de imediato e 20% ficam em Contas a Receber.
    percentual_recebido = float(motor["percentual_inscricoes_recebidas"])
    inscricoes_recebidas = float(receita_inscricoes) * percentual_recebido
    inscricoes_a_receber = float(receita_inscricoes) - inscricoes_recebidas
    motor["inscricoes_recebidas_inicial"] = inscricoes_recebidas
    motor["inscricoes_a_receber_inicial"] = inscricoes_a_receber

    registrar_lancamento(
        motor,
        fase="Receitas",
        categoria="Inscrições",
        descricao="Inscrições recebidas no Banco Conta Movimento",
        tipo="entrada_banco",
        valor=inscricoes_recebidas,
        natureza_dre="receita_operacional",
        origem="cenario",
        metadados={"situacao": "recebido"},
    )
    registrar_lancamento(
        motor,
        fase="Receitas",
        categoria="Inscrições",
        descricao="Inscrições reconhecidas e ainda não recebidas",
        tipo="aumento_contas_receber",
        valor=inscricoes_a_receber,
        natureza_dre="receita_operacional",
        origem="cenario",
        metadados={"situacao": "a_receber"},
    )
    registrar_lancamento(
        motor,
        fase="Receitas",
        categoria="Patrocínio",
        descricao="Patrocínio recebido no Banco Conta Movimento",
        tipo="entrada_banco",
        valor=patrocinio,
        natureza_dre="receita_operacional",
        origem="cenario",
    )
    return motor


def registrar_lancamento(
    motor: Dict[str, Any],
    *,
    fase: str,
    categoria: str,
    descricao: str,
    tipo: str,
    valor: float,
    natureza_dre: str,
    origem: str,
    metadados: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    valor = max(0.0, float(valor))
    lancamento = {
        "ordem": len(motor.setdefault("lancamentos", [])) + 1,
        "data_hora": _agora(),
        "fase": fase,
        "categoria": categoria,
        "descricao": descricao,
        "tipo": tipo,
        "valor": valor,
        "natureza_dre": natureza_dre,
        "origem": origem,
        "metadados": metadados or {},
    }
    motor["lancamentos"].append(lancamento)
    return lancamento


def registrar_planejamento(
    motor: Dict[str, Any],
    escolhas: Dict[str, Dict[str, Any]],
    reserva_planejada: float,
) -> Dict[str, Any]:
    """Registra somente custos efetivamente escolhidos; reserva não é despesa."""
    motor["reserva_planejada"] = max(0.0, float(reserva_planejada))

    for categoria, escolha in escolhas.items():
        registrar_lancamento(
            motor,
            fase="Planejamento",
            categoria=categoria,
            descricao=str(escolha.get("opcao", categoria)),
            tipo="saida_banco",
            valor=float(escolha.get("custo", 0.0)),
            natureza_dre="despesa_operacional",
            origem="escolha_tatica",
            metadados={
                "qualidade": escolha.get("qualidade"),
                "risco": escolha.get("risco"),
            },
        )

    return atualizar_resumo(motor)


def registrar_evento_financeiro(
    motor: Dict[str, Any],
    decisao: Dict[str, Any],
) -> Dict[str, Any]:
    """Registra custos comuns ou efeitos de cancelamento/inadimplência."""
    if decisao.get("tipo_evento") == "cancelamento_inscricoes":
        receita_total_inscricoes = float(motor.get("receita_inscricoes", 0.0))
        recebido_base = float(motor.get("inscricoes_recebidas_inicial", 0.0))
        a_receber_base = float(motor.get("inscricoes_a_receber_inicial", 0.0))

        percentual_reembolso = float(decisao.get("percentual_reembolso_recebido", 0.0))
        percentual_baixa = float(decisao.get("percentual_baixa_a_receber", 0.0))
        valor_reembolso = recebido_base * percentual_reembolso
        valor_baixa = a_receber_base * percentual_baixa

        if valor_reembolso > 0:
            registrar_lancamento(
                motor,
                fase="Execução",
                categoria="Cancelamentos de inscrições",
                descricao=f"{decisao['titulo']}: reembolso de inscrições já pagas",
                tipo="saida_banco",
                valor=valor_reembolso,
                natureza_dre="deducao_receita",
                origem="evento",
                metadados={"evento_id": decisao.get("evento_id")},
            )
        if valor_baixa > 0:
            registrar_lancamento(
                motor,
                fase="Execução",
                categoria="Cancelamentos de inscrições",
                descricao=f"{decisao['titulo']}: baixa de inscrições não recebidas",
                tipo="baixa_contas_receber",
                valor=valor_baixa,
                natureza_dre="deducao_receita",
                origem="evento",
                metadados={"evento_id": decisao.get("evento_id")},
            )
        motor["ultimo_impacto_cancelamento"] = {
            "valor_reembolso": valor_reembolso,
            "valor_baixa_contas_receber": valor_baixa,
            "impacto_total_receita": valor_reembolso + valor_baixa,
            "receita_total_inscricoes": receita_total_inscricoes,
        }
    else:
        registrar_lancamento(
            motor,
            fase="Execução",
            categoria="Evento inesperado",
            descricao=f"{decisao['titulo']}: {decisao['opcao']}",
            tipo="saida_banco",
            valor=float(decisao.get("custo", 0.0)),
            natureza_dre="despesa_operacional",
            origem="evento",
            metadados={
                "evento_id": decisao.get("evento_id"),
                "risco": decisao.get("risco"),
                "qualidade": decisao.get("qualidade"),
            },
        )
    return atualizar_resumo(motor)


def calcular_fluxo_caixa(motor: Dict[str, Any]) -> list[Dict[str, Any]]:
    """Apresenta somente movimentos que efetivamente alteram o Banco Conta Movimento."""
    saldo = 0.0
    linhas: list[Dict[str, Any]] = []
    for item in motor.get("lancamentos", []):
        tipo = item.get("tipo")
        entrada = item["valor"] if tipo in {"entrada_banco", "entrada_caixa"} else 0.0
        saida = item["valor"] if tipo in {"saida_banco", "saida_caixa"} else 0.0
        if entrada == 0 and saida == 0:
            continue
        saldo += entrada - saida
        linhas.append(
            {
                "ordem": item["ordem"],
                "fase": item["fase"],
                "categoria": item["categoria"],
                "descricao": item["descricao"],
                "entrada": entrada,
                "saida": saida,
                "saldo": saldo,
            }
        )
    return linhas


def calcular_dre(motor: Dict[str, Any]) -> Dict[str, float]:
    receita = sum(
        item["valor"]
        for item in motor.get("lancamentos", [])
        if item["natureza_dre"] == "receita_operacional"
    )
    deducoes = sum(
        item["valor"]
        for item in motor.get("lancamentos", [])
        if item["natureza_dre"] == "deducao_receita"
    )
    despesas = sum(
        item["valor"]
        for item in motor.get("lancamentos", [])
        if item["natureza_dre"] == "despesa_operacional"
    )
    resultado = receita - deducoes - despesas
    margem = (resultado / receita * 100) if receita else 0.0
    return {
        "receita_operacional": receita,
        "despesas_operacionais": despesas,
        "resultado_exercicio": resultado,
        "margem_resultado": margem,
    }


def calcular_balanco_simplificado(motor: Dict[str, Any]) -> Dict[str, float]:
    fluxo = calcular_fluxo_caixa(motor)
    saldo_banco = fluxo[-1]["saldo"] if fluxo else 0.0
    contas_receber = sum(
        float(item.get("valor", 0.0))
        for item in motor.get("lancamentos", [])
        if item.get("tipo") == "aumento_contas_receber"
    ) - sum(
        float(item.get("valor", 0.0))
        for item in motor.get("lancamentos", [])
        if item.get("tipo") == "baixa_contas_receber"
    )
    contas_receber = max(0.0, contas_receber)
    aporte = float(motor.get("orcamento_inicial", 0.0))
    resultado = calcular_dre(motor)["resultado_exercicio"]

    ativo_banco = max(0.0, saldo_banco)
    passivo_descoberto = max(0.0, -saldo_banco)
    patrimonio_liquido = aporte + resultado

    return {
        "ativo_banco": ativo_banco,
        "ativo_caixa": ativo_banco,  # compatibilidade com versões anteriores
        "contas_receber": contas_receber,
        "passivo_descoberto": passivo_descoberto,
        "capital_inicial": aporte,
        "resultado_acumulado": resultado,
        "patrimonio_liquido": patrimonio_liquido,
    }


def atualizar_resumo(motor: Dict[str, Any]) -> Dict[str, Any]:
    fluxo = calcular_fluxo_caixa(motor)
    dre = calcular_dre(motor)
    balanco = calcular_balanco_simplificado(motor)
    entradas = sum(item["entrada"] for item in fluxo)
    saidas = sum(item["saida"] for item in fluxo)
    saldo = fluxo[-1]["saldo"] if fluxo else 0.0
    reserva = float(motor.get("reserva_planejada", 0.0))

    resumo = {
        "entradas_caixa": entradas,
        "saidas_caixa": saidas,
        "saldo_banco": saldo,
        "saldo_caixa": saldo,  # compatibilidade
        "reserva_planejada": reserva,
        "banco_livre_apos_reserva": saldo - reserva,
        "caixa_livre_apos_reserva": saldo - reserva,  # compatibilidade
        "modelo_financiamento": motor.get("modelo_financiamento", ""),
        "proposta_financiamento": motor.get("proposta_financiamento", ""),
        "publico_previsto": motor.get("publico_previsto", 0),
        "quantidade_inscritos": motor.get("quantidade_inscritos", 0),
        "valor_inscricao": motor.get("valor_inscricao", 0),
        "dre": dre,
        "balanco": balanco,
    }
    motor["resumo"] = resumo
    return deepcopy(resumo)


def copiar_motor(motor: Dict[str, Any]) -> Dict[str, Any]:
    return deepcopy(motor)


def _classificar_lancamento_dre(item: Dict[str, Any]) -> tuple[str, str]:
    """Classifica o lançamento em uma estrutura pedagógica de DRE para eventos."""
    if item.get("natureza_dre") == "receita_operacional":
        categoria = str(item.get("categoria", "Receita"))
        if categoria == "Inscrições":
            return "Receita Bruta", "Inscrições / ingressos"
        if categoria == "Patrocínio":
            return "Receita Bruta", "Cotas de patrocínio"
        return "Receita Bruta", categoria

    if item.get("natureza_dre") == "deducao_receita":
        return "Deduções", str(item.get("categoria", "Cancelamentos e devoluções"))

    if item.get("tipo") not in {"saida_banco", "saida_caixa"}:
        return "Fora da DRE", str(item.get("categoria", ""))

    categoria = str(item.get("categoria", "Outros"))
    if categoria in {"Infraestrutura", "Equipamentos", "Palestrante", "Alimentação"}:
        return "Custos Diretos", categoria
    if categoria == "Divulgação":
        return "Despesas Operacionais", "Marketing e divulgação"
    if categoria == "Evento inesperado":
        return "Custos Diretos", "Imprevistos da execução"
    return "Despesas Operacionais", categoria


def calcular_dre_analitica(motor: Dict[str, Any]) -> Dict[str, Any]:
    """Gera uma DRE analítica e pedagógica a partir dos lançamentos existentes."""
    linhas: list[Dict[str, Any]] = []
    totais = {
        "receita_bruta": 0.0,
        "deducoes": 0.0,
        "custos_diretos": 0.0,
        "despesas_operacionais": 0.0,
        "resultado_financeiro": 0.0,
        "tributos_lucro": 0.0,
    }

    for item in motor.get("lancamentos", []):
        grupo, conta = _classificar_lancamento_dre(item)
        if grupo == "Fora da DRE":
            continue

        valor = float(item.get("valor", 0.0))
        chave_total = {
            "Receita Bruta": "receita_bruta",
            "Deduções": "deducoes",
            "Custos Diretos": "custos_diretos",
            "Despesas Operacionais": "despesas_operacionais",
        }.get(grupo)
        if chave_total:
            totais[chave_total] += valor

        linhas.append(
            {
                "Grupo": grupo,
                "Conta": conta,
                "Origem": item.get("descricao", ""),
                "Valor": valor,
            }
        )

    receita_liquida = totais["receita_bruta"] - totais["deducoes"]
    lucro_bruto = receita_liquida - totais["custos_diretos"]
    resultado_operacional = lucro_bruto - totais["despesas_operacionais"]
    lair = resultado_operacional + totais["resultado_financeiro"]
    lucro_liquido = lair - totais["tributos_lucro"]
    margem = (lucro_liquido / receita_liquida * 100) if receita_liquida else 0.0

    return {
        "linhas": linhas,
        **totais,
        "receita_liquida": receita_liquida,
        "lucro_bruto": lucro_bruto,
        "resultado_operacional": resultado_operacional,
        "lair": lair,
        "lucro_liquido": lucro_liquido,
        "margem_liquida": margem,
    }


def calcular_balanco_analitico(motor: Dict[str, Any]) -> Dict[str, Any]:
    """Gera posição patrimonial simplificada e conciliada do projeto."""
    resumo = calcular_balanco_simplificado(motor)
    ativo = [
        {
            "Grupo": "Ativo Circulante",
            "Conta": "Banco Conta Movimento",
            "Origem": "Saldo final das movimentações bancárias",
            "Valor": resumo["ativo_banco"],
        },
        {
            "Grupo": "Ativo Circulante",
            "Conta": "Contas a receber: inscrições",
            "Origem": "Inscrições reconhecidas e ainda não recebidas",
            "Valor": resumo["contas_receber"],
        },
        {
            "Grupo": "Ativo Circulante",
            "Conta": "Estoques / materiais",
            "Origem": "Não utilizado nesta versão da simulação",
            "Valor": 0.0,
        },
    ]
    passivo = [
        {
            "Grupo": "Passivo Circulante",
            "Conta": "Saldo descoberto / necessidade de financiamento",
            "Origem": "Insuficiência de caixa, quando existente",
            "Valor": resumo["passivo_descoberto"],
        },
        {
            "Grupo": "Passivo Circulante",
            "Conta": "Fornecedores, salários e tributos a pagar",
            "Origem": "Não utilizados nesta versão da simulação",
            "Valor": 0.0,
        },
    ]
    patrimonio = [
        {
            "Grupo": "Patrimônio Líquido",
            "Conta": "Capital inicial do projeto",
            "Origem": "Recursos iniciais disponibilizados",
            "Valor": resumo["capital_inicial"],
        },
        {
            "Grupo": "Patrimônio Líquido",
            "Conta": "Resultado acumulado do projeto",
            "Origem": "Lucro ou prejuízo apurado na DRE",
            "Valor": resumo["resultado_acumulado"],
        },
    ]

    total_ativo = sum(x["Valor"] for x in ativo)
    total_passivo = sum(x["Valor"] for x in passivo)
    total_pl = sum(x["Valor"] for x in patrimonio)
    return {
        "ativo": ativo,
        "passivo": passivo,
        "patrimonio": patrimonio,
        "total_ativo": total_ativo,
        "total_passivo": total_passivo,
        "total_patrimonio": total_pl,
        "total_passivo_pl": total_passivo + total_pl,
    }


def analisar_resultados_financeiros(motor: Dict[str, Any]) -> Dict[str, list[str]]:
    """Produz observações automáticas, transparentes e sem IA generativa."""
    fluxo = calcular_fluxo_caixa(motor)
    dre = calcular_dre_analitica(motor)
    bp = calcular_balanco_analitico(motor)

    fluxo_obs: list[str] = []
    saldos = [float(x["saldo"]) for x in fluxo]
    saldo_final = saldos[-1] if saldos else 0.0
    menor_saldo = min(saldos) if saldos else 0.0
    if menor_saldo < 0:
        fluxo_obs.append("Em algum momento, o projeto apresentou insuficiência de caixa.")
    else:
        fluxo_obs.append("O projeto manteve saldo bancário não negativo durante toda a simulação.")
    fluxo_obs.append(
        f"O saldo final foi de {_moeda_br(saldo_final)}, após todas as entradas e saídas registradas."
    )

    dre_obs: list[str] = []
    if dre["lucro_liquido"] >= 0:
        dre_obs.append("O projeto apresentou resultado econômico positivo.")
    else:
        dre_obs.append("O projeto apresentou prejuízo econômico.")
    if dre["linhas"]:
        despesas = [x for x in dre["linhas"] if x["Grupo"] != "Receita Bruta"]
        if despesas:
            maior = max(despesas, key=lambda x: x["Valor"])
            dre_obs.append(
                f"O maior gasto identificado foi {maior['Conta']}, no valor de {_moeda_br(maior['Valor'])}."
            )
    dre_obs.append(f"A margem líquida apurada foi de {_percentual_br(dre['margem_liquida'])}.")

    bp_obs: list[str] = []
    if bp["total_patrimonio"] >= 0:
        bp_obs.append("O patrimônio líquido do projeto permaneceu positivo.")
    else:
        bp_obs.append("O patrimônio líquido ficou negativo, indicando consumo superior aos recursos próprios.")
    if bp["total_passivo"] > 0:
        bp_obs.append("Foi reconhecida uma necessidade de financiamento decorrente de saldo bancário negativo.")
    else:
        bp_obs.append("Não foi reconhecida necessidade de financiamento ao final da simulação.")
    bp_obs.append("Nesta versão, o ativo é formado pelo Banco Conta Movimento e pelas inscrições ainda a receber.")

    return {"fluxo": fluxo_obs, "dre": dre_obs, "balanco": bp_obs}


def calcular_indicadores_analiticos(motor: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula indicadores pedagógicos com memória de cálculo e tratamento de bases nulas."""
    dre = calcular_dre_analitica(motor)
    bp = calcular_balanco_analitico(motor)
    fluxo = calcular_fluxo_caixa(motor)

    capital_inicial = float(motor.get("orcamento_inicial", 0.0))
    reserva = float(motor.get("reserva_planejada", 0.0))
    receita_inscricoes = sum(
        float(item.get("valor", 0.0))
        for item in motor.get("lancamentos", [])
        if item.get("natureza_dre") == "receita_operacional"
        and item.get("categoria") == "Inscrições"
    )
    saidas = [
        item for item in motor.get("lancamentos", [])
        if item.get("tipo") in {"saida_banco", "saida_caixa"}
    ]
    total_gastos = sum(float(item.get("valor", 0.0)) for item in saidas)
    maior_gasto = max(
        (float(item.get("valor", 0.0)) for item in saidas),
        default=0.0,
    )
    custos_imprevistos = sum(
        float(item.get("valor", 0.0))
        for item in saidas
        if item.get("origem") == "evento"
    )
    saldo_final = float(fluxo[-1]["saldo"]) if fluxo else 0.0

    def percentual(numerador: float, denominador: float) -> float | None:
        return (numerador / denominador * 100.0) if denominador else None

    margem = percentual(dre["lucro_liquido"], dre["receita_liquida"])
    roi = percentual(dre["lucro_liquido"], capital_inicial)
    comprometimento = percentual(total_gastos, capital_inicial)
    participacao_maior = percentual(maior_gasto, total_gastos)
    dependencia_inscricoes = percentual(receita_inscricoes, dre["receita_bruta"])
    cobertura_reserva = percentual(reserva, custos_imprevistos)

    ativo_circulante = float(bp["total_ativo"])
    passivo_circulante = float(bp["total_passivo"])
    liquidez = (ativo_circulante / passivo_circulante) if passivo_circulante else None

    indicadores = [
        {
            "Indicador": "Margem líquida",
            "Fórmula": "Lucro líquido ÷ Receita líquida × 100",
            "Memória de cálculo": f"{_moeda_br(dre['lucro_liquido'])} ÷ {_moeda_br(dre['receita_liquida'])} × 100",
            "Resultado": margem,
            "Unidade": "%",
        },
        {
            "Indicador": "Retorno sobre o capital inicial (ROI)",
            "Fórmula": "Lucro líquido ÷ Capital inicial × 100",
            "Memória de cálculo": f"{_moeda_br(dre['lucro_liquido'])} ÷ {_moeda_br(capital_inicial)} × 100",
            "Resultado": roi,
            "Unidade": "%",
        },
        {
            "Indicador": "Comprometimento do orçamento inicial",
            "Fórmula": "Gastos totais ÷ Capital inicial × 100",
            "Memória de cálculo": f"{_moeda_br(total_gastos)} ÷ {_moeda_br(capital_inicial)} × 100",
            "Resultado": comprometimento,
            "Unidade": "%",
        },
        {
            "Indicador": "Cobertura da reserva para imprevistos",
            "Fórmula": "Reserva planejada ÷ Gastos com imprevistos × 100",
            "Memória de cálculo": (
                f"{_moeda_br(reserva)} ÷ {_moeda_br(custos_imprevistos)} × 100"
                if custos_imprevistos else "Não houve gasto classificado como imprevisto"
            ),
            "Resultado": cobertura_reserva,
            "Unidade": "%",
        },
        {
            "Indicador": "Participação do maior gasto",
            "Fórmula": "Maior gasto ÷ Gastos totais × 100",
            "Memória de cálculo": f"{_moeda_br(maior_gasto)} ÷ {_moeda_br(total_gastos)} × 100",
            "Resultado": participacao_maior,
            "Unidade": "%",
        },
        {
            "Indicador": "Dependência das inscrições",
            "Fórmula": "Receita de inscrições ÷ Receita bruta × 100",
            "Memória de cálculo": f"{_moeda_br(receita_inscricoes)} ÷ {_moeda_br(dre['receita_bruta'])} × 100",
            "Resultado": dependencia_inscricoes,
            "Unidade": "%",
        },
        {
            "Indicador": "Liquidez do projeto",
            "Fórmula": "Ativo circulante ÷ Passivo circulante",
            "Memória de cálculo": (
                f"{_moeda_br(ativo_circulante)} ÷ {_moeda_br(passivo_circulante)}"
                if passivo_circulante else "Não há passivo circulante ao final da simulação"
            ),
            "Resultado": liquidez,
            "Unidade": "índice",
        },
    ]

    observacoes: list[str] = []
    if margem is None:
        observacoes.append("A margem líquida não pôde ser calculada porque não houve receita líquida.")
    elif margem >= 0:
        observacoes.append(f"A cada R$ 100,00 de receita líquida, o projeto gerou R$ {margem:.2f} de resultado líquido.")
    else:
        observacoes.append(f"A cada R$ 100,00 de receita líquida, o projeto perdeu R$ {abs(margem):.2f}.")

    if comprometimento is not None:
        if comprometimento > 100:
            observacoes.append("Os gastos superaram o capital inicial; as receitas do evento foram necessárias para sustentar a execução.")
        else:
            observacoes.append(f"Os gastos consumiram {comprometimento:.1f}% do capital inicial disponibilizado.")

    if custos_imprevistos <= 0:
        observacoes.append("Não houve gasto com imprevistos; por isso, a cobertura da reserva não se aplica.")
    elif cobertura_reserva is not None and cobertura_reserva >= 100:
        observacoes.append("A reserva planejada seria suficiente para cobrir integralmente os gastos com imprevistos.")
    else:
        observacoes.append("A reserva planejada não seria suficiente para cobrir integralmente os gastos com imprevistos.")

    if dependencia_inscricoes is not None:
        observacoes.append(f"As inscrições representaram {dependencia_inscricoes:.1f}% da receita bruta do projeto.")

    if liquidez is None:
        observacoes.append("Não há passivo circulante no encerramento; o índice de liquidez não é aplicável.")
    elif liquidez >= 1:
        observacoes.append(f"Para cada R$ 1,00 de obrigação, o projeto possui R$ {liquidez:.2f} em ativo circulante.")
    else:
        observacoes.append(f"Para cada R$ 1,00 de obrigação, o projeto possui apenas R$ {liquidez:.2f} em ativo circulante.")

    return {
        "linhas": indicadores,
        "observacoes": observacoes,
        "bases": {
            "capital_inicial": capital_inicial,
            "reserva_planejada": reserva,
            "receita_inscricoes": receita_inscricoes,
            "total_gastos": total_gastos,
            "maior_gasto": maior_gasto,
            "custos_imprevistos": custos_imprevistos,
            "saldo_final": saldo_final,
        },
    }
