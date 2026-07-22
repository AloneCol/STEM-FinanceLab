from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any, Dict, Iterable
from core.config import APP_VERSION


def _moeda(valor: Any) -> str:
    try:
        numero = float(valor or 0)
    except (TypeError, ValueError):
        numero = 0.0
    texto = f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def _lista_html(itens: Iterable[str]) -> str:
    itens = list(itens or [])
    if not itens:
        return "<p>Não há registros para esta seção.</p>"
    return "<ul>" + "".join(f"<li>{escape(str(item))}</li>" for item in itens) + "</ul>"


def _tabela_html(cabecalhos: list[str], linhas: list[list[Any]]) -> str:
    th = "".join(f"<th>{escape(str(c))}</th>" for c in cabecalhos)
    corpo = []
    for linha in linhas:
        corpo.append("<tr>" + "".join(f"<td>{escape(str(v))}</td>" for v in linha) + "</tr>")
    return f"<table><thead><tr>{th}</tr></thead><tbody>{''.join(corpo)}</tbody></table>"


def gerar_relatorio_html(
    *,
    perfil: Dict[str, Any],
    tentativa: int,
    resumo: Dict[str, Any],
    fluxo: list[Dict[str, Any]],
    dre: Dict[str, Any],
    balanco: Dict[str, Any],
    indicadores: Dict[str, Any],
    feedback: Dict[str, Any],
    decisoes_eventos: list[Dict[str, Any]],
    tutor_ia: str = "",
) -> bytes:
    fluxo_linhas = [
        [
            item.get("fase", ""),
            item.get("descricao", ""),
            _moeda(item.get("entrada")),
            _moeda(item.get("saida")),
            _moeda(item.get("saldo")),
        ]
        for item in fluxo
    ]

    eventos_linhas = [
        [
            item.get("titulo", ""),
            item.get("opcao", ""),
            _moeda(item.get("custo")),
            item.get("risco", ""),
            item.get("qualidade", ""),
        ]
        for item in decisoes_eventos
    ]

    indicadores_linhas = []
    for item in indicadores.get("linhas", []):
        resultado = item.get("Resultado")
        if resultado is None:
            resultado_formatado = "Não aplicável"
        elif item.get("Unidade") == "%":
            resultado_formatado = f"{float(resultado):.2f}%".replace(".", ",")
        else:
            resultado_formatado = f"{float(resultado):.2f}".replace(".", ",")
        indicadores_linhas.append([
            item.get("Indicador", ""),
            item.get("Fórmula", ""),
            resultado_formatado,
        ])

    tutor_secao = ""
    if tutor_ia:
        tutor_secao = f"<h2>Tutor Inteligente</h2><div class='box'>{escape(tutor_ia).replace(chr(10), '<br>')}</div>"

    html = f"""<!doctype html>
<html lang='pt-BR'>
<head>
<meta charset='utf-8'>
<title>Relatório STEM FinanceLab</title>
<style>
body{{font-family:Arial,sans-serif;max-width:1000px;margin:32px auto;color:#1f2937;line-height:1.45}}
h1,h2,h3{{color:#123b5d}} .muted{{color:#64748b}} .cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
.card,.box{{border:1px solid #d7dee7;border-radius:10px;padding:14px;background:#f8fafc}} .card strong{{display:block;font-size:1.15rem;margin-top:5px}}
table{{width:100%;border-collapse:collapse;margin:12px 0 24px}} th,td{{border:1px solid #d7dee7;padding:8px;text-align:left;font-size:13px}} th{{background:#eaf1f7}}
section{{margin-top:28px}} @media print{{body{{margin:10mm}} .cards{{grid-template-columns:repeat(2,1fr)}}}}
</style>
</head>
<body>
<h1>STEM FinanceLab: Relatório da Simulação</h1>
<p class='muted'>Versão {APP_VERSION} · Tentativa {tentativa} · Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>

<section><h2>Identificação do participante</h2>
<p><strong>Gestor:</strong> {escape(str(perfil.get('nome', 'Não informado')))} · <strong>Instituição:</strong> {escape(str(perfil.get('instituicao') or 'Não informada'))} · <strong>Curso:</strong> {escape(str(perfil.get('curso') or 'Não informado'))}</p>
<p><strong>Área:</strong> {escape(str(perfil.get('area', 'Não informado')))} · <strong>Vínculo:</strong> {escape(str(perfil.get('perfil', 'Não informado')))} · <strong>Experiência:</strong> {escape(str(perfil.get('experiencia', 'Não informado')))} · <strong>Gestão de recursos:</strong> {escape(str(perfil.get('experiencia_gestao', 'Não informado')))}</p></section>

<section><h2>Estratégia de financiamento</h2><p><strong>Modelo:</strong> {escape(str(resumo.get('modelo_financiamento', 'Não informado')))} · <strong>Proposta:</strong> {escape(str(resumo.get('proposta_financiamento', 'Não informada')))} · <strong>Público previsto:</strong> {escape(str(resumo.get('publico_previsto', 'Não informado')))} · <strong>Pagantes:</strong> {escape(str(resumo.get('quantidade_inscritos', 'Não informado')))}</p></section>

<section><h2>Resumo executivo</h2><div class='cards'>
<div class='card'>Entradas no banco<strong>{_moeda(resumo.get('entradas_caixa'))}</strong></div>
<div class='card'>Saídas do banco<strong>{_moeda(resumo.get('saidas_caixa'))}</strong></div>
<div class='card'>Saldo bancário<strong>{_moeda(resumo.get('saldo_caixa'))}</strong></div>
<div class='card'>Lucro líquido<strong>{_moeda(dre.get('lucro_liquido'))}</strong></div>
</div></section>

<section><h2>Decisões diante dos eventos</h2>{_tabela_html(['Evento','Decisão','Custo','Risco','Qualidade'], eventos_linhas)}</section>
<section><h2>Fluxo de Caixa</h2>{_tabela_html(['Fase','Descrição','Entrada','Saída','Saldo'], fluxo_linhas)}</section>
<section><h2>Demonstração do Resultado</h2>
{_tabela_html(['Descrição','Valor'], [
['Receita bruta', _moeda(dre.get('receita_bruta'))],
['Deduções', _moeda(dre.get('deducoes'))],
['Receita líquida', _moeda(dre.get('receita_liquida'))],
['Custos diretos', _moeda(dre.get('custos_diretos'))],
['Despesas operacionais', _moeda(dre.get('despesas_operacionais'))],
['Lucro líquido', _moeda(dre.get('lucro_liquido'))],
])}</section>
<section><h2>Balanço Patrimonial Simplificado</h2>
{_tabela_html(['Grupo','Valor'], [
['Total do Ativo', _moeda(balanco.get('total_ativo'))],
['Total do Passivo', _moeda(balanco.get('total_passivo'))],
['Patrimônio Líquido', _moeda(balanco.get('total_patrimonio'))],
['Passivo + Patrimônio Líquido', _moeda(balanco.get('total_passivo_pl'))],
])}</section>
<section><h2>Indicadores</h2>{_tabela_html(['Indicador','Fórmula','Resultado'], indicadores_linhas)}</section>
<section><h2>Reflexão pedagógica</h2>
<h3>Resultado</h3>{_lista_html(feedback.get('fatos', []))}
<h3>O que contribuiu positivamente</h3>{_lista_html(feedback.get('acertos', []))}
<h3>Pontos de atenção</h3>{_lista_html(feedback.get('atencao', []))}
<h3>O que fazer na próxima tentativa</h3>{_lista_html(feedback.get('recomendacoes', []))}
</section>
{tutor_secao}
</body></html>"""
    return html.encode("utf-8")
