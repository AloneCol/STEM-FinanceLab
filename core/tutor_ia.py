from __future__ import annotations

import os
from typing import Any, Dict

import streamlit as st
from openai import OpenAI


INSTRUCOES_TUTOR = """
Você é o Tutor Inteligente do STEM FinanceLab, um Serious Game educacional.
Sua função é interpretar pedagogicamente resultados financeiros que já foram
calculados por um motor determinístico.

Regras obrigatórias:
- Não refaça cálculos e não invente valores.
- Não altere os resultados apresentados.
- Não use linguagem punitiva, alarmista ou excessivamente técnica.
- Relacione decisões, consequências e possibilidades de melhoria.
- Produza feedback em português do Brasil, claro e adequado a estudantes e
  profissionais STEM.
- Utilize no máximo 180 palavras.
- Organize a resposta exatamente nestas quatro seções, em Markdown:
  **Leitura do resultado**
  **Decisão de maior impacto**
  **Estratégia para a próxima tentativa**
  **Pergunta para reflexão**
""".strip()


def _obter_configuracao() -> tuple[str | None, str]:
    """Obtém chave e modelo sem expor a credencial na interface."""
    chave = None
    modelo = "gpt-5-mini"

    try:
        chave = st.secrets.get("OPENAI_API_KEY")
        modelo = st.secrets.get("OPENAI_MODEL", modelo)
    except Exception:
        # O arquivo secrets.toml pode não existir durante desenvolvimento local.
        pass

    chave = chave or os.getenv("OPENAI_API_KEY")
    modelo = os.getenv("OPENAI_MODEL", modelo)
    return chave, modelo


def tutor_disponivel() -> bool:
    chave, _ = _obter_configuracao()
    return bool(chave and chave != "cole_sua_chave_aqui")


def _maiores_gastos(motor: Dict[str, Any], limite: int = 3) -> list[dict[str, Any]]:
    gastos = [
        {
            "descricao": str(item.get("descricao", "Despesa")),
            "categoria": str(item.get("categoria", "Sem categoria")),
            "valor": float(item.get("valor", 0.0)),
        }
        for item in motor.get("lancamentos", [])
        if item.get("tipo") in {"saida_banco", "saida_caixa"}
    ]
    return sorted(gastos, key=lambda item: item["valor"], reverse=True)[:limite]


def montar_resumo_tutor(
    motor: Dict[str, Any],
    resumo: Dict[str, Any],
    dre: Dict[str, Any],
    indicadores: Dict[str, Any],
    feedback_regras: Dict[str, Any],
) -> str:
    """Monta fatos calculados para interpretação da IA, sem solicitar cálculos."""
    linhas_indicadores = []
    for item in indicadores.get("linhas", []):
        resultado = item.get("Resultado")
        valor = "não aplicável" if resultado is None else str(round(float(resultado), 2))
        unidade = item.get("Unidade", "")
        linhas_indicadores.append(f"- {item.get('Indicador')}: {valor}{unidade}")

    gastos = _maiores_gastos(motor)
    linhas_gastos = [
        f"- {item['categoria']} — {item['descricao']}: R$ {item['valor']:.2f}"
        for item in gastos
    ] or ["- Nenhuma saída financeira registrada."]

    return f"""
DADOS CALCULADOS PELO MOTOR FINANCEIRO — NÃO RECALCULAR
Tentativa: {st.session_state.get('numero_tentativa', 1)}
Receita bruta: R$ {float(dre.get('receita_bruta', 0.0)):.2f}
Despesas operacionais: R$ {float(dre.get('despesas_operacionais', 0.0)):.2f}
Lucro líquido: R$ {float(dre.get('lucro_liquido', 0.0)):.2f}
Saldo bancário final: R$ {float(resumo.get('saldo_caixa', 0.0)):.2f}
Reserva planejada: R$ {float(resumo.get('reserva_planejada', 0.0)):.2f}
Caixa livre após reserva: R$ {float(resumo.get('caixa_livre_apos_reserva', 0.0)):.2f}
Contas a receber: R$ {float(resumo.get('contas_receber', 0.0)):.2f}

MAIORES GASTOS REGISTRADOS
{chr(10).join(linhas_gastos)}

INDICADORES JÁ CALCULADOS
{chr(10).join(linhas_indicadores)}

INTERPRETAÇÃO DO SISTEMA BASEADO EM REGRAS
Pontos positivos: {'; '.join(feedback_regras.get('acertos', []))}
Pontos de atenção: {'; '.join(feedback_regras.get('atencao', []))}
Recomendações: {'; '.join(feedback_regras.get('recomendacoes', []))}

Produza somente o feedback pedagógico solicitado nas instruções.
""".strip()


def gerar_feedback_tutor_ia(
    motor: Dict[str, Any],
    resumo: Dict[str, Any],
    dre: Dict[str, Any],
    indicadores: Dict[str, Any],
    feedback_regras: Dict[str, Any],
) -> str:
    chave, modelo = _obter_configuracao()
    if not chave or chave == "cole_sua_chave_aqui":
        raise RuntimeError(
            "A chave OPENAI_API_KEY ainda não foi configurada em .streamlit/secrets.toml."
        )

    cliente = OpenAI(api_key=chave, timeout=30.0, max_retries=1)
    resumo_tutor = montar_resumo_tutor(
        motor, resumo, dre, indicadores, feedback_regras
    )

    resposta = cliente.responses.create(
        model=modelo,
        instructions=INSTRUCOES_TUTOR,
        input=resumo_tutor,
        max_output_tokens=350,
    )

    texto = (resposta.output_text or "").strip()
    if not texto:
        raise RuntimeError("A API não retornou um texto de feedback.")
    return texto


def mensagem_amigavel_erro_tutor(erro: Exception) -> str:
    """Converte falhas técnicas em mensagens adequadas ao participante."""
    texto = str(erro).lower()

    if "insufficient_quota" in texto or "exceeded your current quota" in texto:
        return (
            "O Tutor Inteligente está temporariamente indisponível porque a conta "
            "utilizada para acessar a API não possui créditos ativos. A simulação e "
            "a análise pedagógica baseada em regras continuam disponíveis normalmente."
        )
    if "invalid_api_key" in texto or "incorrect api key" in texto or "401" in texto:
        return (
            "O Tutor Inteligente não pôde ser acessado porque a chave da API precisa "
            "ser revisada. A análise pedagógica baseada em regras permanece disponível."
        )
    if "timeout" in texto or "timed out" in texto:
        return (
            "O Tutor Inteligente demorou mais do que o esperado para responder. "
            "Tente novamente em alguns instantes."
        )
    if "connection" in texto or "network" in texto:
        return (
            "Não foi possível conectar ao Tutor Inteligente neste momento. Verifique a "
            "conexão com a internet e tente novamente."
        )
    return (
        "O Tutor Inteligente está temporariamente indisponível. A simulação continua "
        "válida e a análise pedagógica baseada em regras pode ser utilizada normalmente."
    )


def montar_feedback_contingencia(feedback_regras: Dict[str, Any]) -> str:
    """Monta orientação local quando a API não puder ser utilizada."""
    acertos = feedback_regras.get("acertos", [])
    atencao = feedback_regras.get("atencao", [])
    recomendacoes = feedback_regras.get("recomendacoes", [])

    positivo = acertos[0] if acertos else "A tentativa gerou dados suficientes para análise."
    alerta = atencao[0] if atencao else "Não foram identificados alertas críticos nesta tentativa."
    proximo = (
        recomendacoes[0]
        if recomendacoes
        else "Compare o resultado com uma nova estratégia de planejamento."
    )

    return (
        "**Orientação alternativa do sistema**\n\n"
        f"- **Aspecto positivo:** {positivo}\n"
        f"- **Ponto de atenção:** {alerta}\n"
        f"- **Próxima tentativa:** {proximo}\n\n"
        "*Esta orientação foi produzida pelo sistema baseado em regras, sem uso de IA.*"
    )
