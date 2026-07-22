import logging

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from core.config import APP_VERSION
from core.logging_config import configurar_logs
from core.database import (
    inicializar_banco,
    salvar_participante,
    salvar_diagnostico,
    salvar_planejamento,
    salvar_evento,
    iniciar_simulacao,
    finalizar_simulacao,
    interromper_simulacao,
    salvar_estrategia_financiamento,
)
from core.session import inicializar_sessao
from core.feedback import gerar_feedback_aprendizagem
from core.tutor_ia import (
    gerar_feedback_tutor_ia,
    mensagem_amigavel_erro_tutor,
    montar_feedback_contingencia,
    tutor_disponivel,
)
from core.relatorio import gerar_relatorio_html
from core.ui import aplicar_estilo, cabecalho, rodape
from core.financeiro import (
    calcular_saldo_planejamento,
    calcular_resumo_planejamento,
    validar_alocacoes,
    validar_escolhas_taticas,
    analisar_riscos_alocacoes,
    analisar_riscos_escolhas_taticas,
    calcular_receita_total,
    calcular_recursos_disponiveis,
)
from core.eventos import sortear_eventos, obter_evento
from core.motor_financeiro import (
    criar_motor_financeiro,
    registrar_planejamento,
    registrar_evento_financeiro,
    calcular_fluxo_caixa,
    atualizar_resumo,
    calcular_dre_analitica,
    calcular_balanco_analitico,
    analisar_resultados_financeiros,
    calcular_indicadores_analiticos,
)
from data.questionario import QUESTOES_DIAGNOSTICO
from data.cenario import (
    CATEGORIAS,
    CENARIOS,
    obter_cenario,
    obter_opcoes_taticas,
    obter_modelos_financiamento,
    obter_propostas_financiamento,
)
from data.conceitos import CONCEITOS

configurar_logs()
logger = logging.getLogger(__name__)


def rolar_para_topo() -> None:
    """Reposiciona a tela no início após a troca de etapa em dispositivos móveis."""
    components.html(
        """
        <script>
            window.parent.scrollTo({top: 0, left: 0, behavior: 'instant'});
        </script>
        """,
        height=0,
        width=0,
    )

st.set_page_config(
    page_title="STEM FinanceLab: Jogo Estratégico",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

try:
    inicializar_banco()
except Exception:
    logger.exception("Falha ao inicializar o banco de dados")
    st.error("Não foi possível preparar o armazenamento da aplicação. Tente novamente em instantes.")
    st.stop()

inicializar_sessao()
aplicar_estilo()


def ir_para(etapa: str) -> None:
    st.session_state.etapa = etapa
    st.rerun()


def encerrar_para_agradecimento(motivo: str) -> None:
    """Finaliza a sessão visual sem depender do fechamento do navegador."""
    nome = st.session_state.get("perfil_participante", {}).get("nome", "Participante")
    st.session_state.clear()
    st.session_state.etapa = "agradecimento"
    st.session_state.nome_agradecimento = nome
    st.session_state.motivo_encerramento = motivo
    st.rerun()


def controle_encerramento_durante_missao() -> None:
    """Exibe uma saída discreta e exige confirmação antes de interromper a tentativa."""
    col_espaco, col_acao = st.columns([5, 1])
    with col_acao:
        if st.button("🚪 Encerrar sessão", key="abrir_confirmacao_encerramento", width="stretch"):
            st.session_state.confirmar_encerramento = True

    if st.session_state.get("confirmar_encerramento"):
        st.warning(
            "Deseja realmente encerrar esta missão? A tentativa será registrada como interrompida."
        )
        col_continuar, col_encerrar = st.columns(2)
        with col_continuar:
            if st.button("Continuar missão", key="cancelar_encerramento", width="stretch"):
                st.session_state.confirmar_encerramento = False
                st.rerun()
        with col_encerrar:
            if st.button(
                "Confirmar encerramento",
                key="confirmar_encerramento_definitivo",
                type="primary",
                width="stretch",
            ):
                simulacao_id = st.session_state.get("simulacao_id")
                if simulacao_id:
                    interromper_simulacao(int(simulacao_id))
                encerrar_para_agradecimento("interrompida")

def exibir_conceito(chave: str) -> None:
    conceito = CONCEITOS[chave]

    with st.expander(f"📘 {conceito['titulo']}"):
        st.markdown("**O que é?**")
        st.write(conceito["definicao"])

        st.markdown("**Aplicação no simulador**")
        st.write(conceito["aplicacao"])

        st.markdown("**Por que é importante?**")
        st.write(conceito["importancia"])

        st.link_button(
            "Aprofundar conhecimento",
            conceito["link"],
            width='stretch',
        )




TERMOS_EDUCACIONAIS = {
    "roi": (
        "ROI significa Retorno sobre o Investimento. Neste simulador, ele compara "
        "o lucro ou prejuízo obtido com o capital inicial destinado ao projeto. "
        "Um valor positivo representa retorno; um valor negativo representa perda."
    ),
    "ativo": (
        "O Ativo representa os bens e direitos controlados pelo projeto, como dinheiro "
        "em caixa, valores a receber, materiais e outros recursos com potencial de gerar benefícios."
    ),
    "passivo": (
        "O Passivo representa as obrigações do projeto, como valores devidos a fornecedores, "
        "tributos, salários, empréstimos e outras contas a pagar."
    ),
    "patrimonio_liquido": (
        "O Patrimônio Líquido corresponde aos recursos próprios do projeto após a dedução "
        "das obrigações. No simulador, reúne o capital inicial e o resultado obtido."
    ),
    "margem_liquida": (
        "A Margem Líquida indica qual percentual da receita líquida permaneceu como lucro "
        "após a dedução dos custos e das despesas. Quanto maior e positiva, maior foi a "
        "capacidade do projeto de transformar receita em resultado; valores negativos "
        "representam prejuízo."
    ),
}


def exibir_titulo_com_ajuda(titulo: str, explicacao: str, nivel: str = "####") -> None:
    col_titulo, col_ajuda = st.columns([12, 1], vertical_alignment="center")
    with col_titulo:
        st.markdown(f"{nivel} {titulo}")
    with col_ajuda:
        with st.popover("ⓘ"):
            st.write(explicacao)


def pagina_inicial() -> None:
    cabecalho()

    st.markdown(
        """
        <div class="hero-subtitle">
            Bem-vindo ao STEM FinanceLab. Assuma o papel de gestor financeiro,
            administre recursos limitados e acompanhe as consequências de cada decisão.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="info-card">
            <h3>Sua experiência nesta missão</h3>
            <p>
                Você será responsável pela organização financeira de um evento. Ao longo do jogo,
                suas decisões influenciarão o orçamento, o fluxo de caixa, a Demonstração do Resultado
                e o Balanço Patrimonial.
            </p>
            <p>
                Ao final, você poderá analisar seu desempenho, refletir sobre as escolhas realizadas
                e identificar como aperfeiçoar sua estratégia em uma nova tentativa.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_tempo, col_objetivo, col_alerta = st.columns(3)
    with col_tempo:
        st.info("⏱️ **Tempo estimado:** 20 a 25 minutos")
    with col_objetivo:
        st.success("🎯 **Objetivo:** concluir a missão com equilíbrio financeiro")
    with col_alerta:
        st.warning("⚠️ **Atenção:** cada decisão poderá alterar o resultado")

    col_apresentacao, col_missao = st.columns([1.05, 1])
    with col_apresentacao:
        st.markdown(
            """
            <div class="info-card">
                <h3>Sobre o jogo</h3>
                <p>
                    O STEM FinanceLab é um jogo estratégico de gerenciamento de recursos
                    voltado ao ensino de princípios financeiros a profissionais e estudantes
                    das áreas STEM.
                </p>
                <p>
                    Em um ambiente seguro, você poderá planejar, decidir, enfrentar desafios
                    e aprender com os efeitos financeiros das próprias escolhas.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_missao:
        st.markdown(
            """
            <div class="info-card">
                <h3>Como funciona</h3>
                <p>1. Identificação do gestor</p>
                <p>2. Diagnóstico inicial</p>
                <p>3. Apresentação da missão</p>
                <p>4. Planejamento e decisões</p>
                <p>5. Desafios estratégicos</p>
                <p>6. Resultados e reflexão</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("ℹ️ Sobre esta pesquisa"):
        st.write(
            "O STEM FinanceLab é um artefato desenvolvido no âmbito de um Mestrado Profissional. "
            "Seu objetivo é apoiar o ensino de princípios financeiros por meio de um Serious Game "
            "aplicado a profissionais e estudantes das áreas STEM."
        )
        st.write(
            "A participação na simulação contribui para a avaliação do artefato e para sua evolução "
            "como ferramenta educacional."
        )

    st.markdown("### Identificação do gestor")
    with st.form("form_identificacao", clear_on_submit=False):
        nome = st.text_input("Nome ou identificação do participante *", max_chars=100)
        c1, c2 = st.columns(2)
        with c1:
            instituicao = st.text_input("Instituição (opcional)", max_chars=120)
            curso = st.text_input("Curso ou área de formação (opcional)", max_chars=120)
            area = st.selectbox(
                "Área principal",
                ["Computação", "Engenharia", "Matemática", "Ciências Naturais", "Tecnologia", "Outra área STEM"],
            )
        with c2:
            perfil = st.selectbox("Vínculo principal", ["Estudante", "Professor(a)", "Profissional"])
            experiencia = st.selectbox(
                "Tempo de experiência",
                ["Sem experiência profissional", "Menos de 1 ano", "1 a 2 anos", "3 a 5 anos", "6 a 10 anos", "Mais de 10 anos"],
            )
            experiencia_gestao = st.selectbox(
                "Experiência com gestão de recursos", ["Nenhuma", "Baixa", "Moderada", "Alta"]
            )

        st.markdown("### Selecione sua missão")
        missao = st.radio(
            "Escolha o porte do projeto que deseja administrar",
            options=list(CENARIOS.keys()),
            format_func=lambda chave: f"{CENARIOS[chave]['nome']} (porte {CENARIOS[chave]['porte'].lower()})",
            horizontal=True,
        )
        cenario = obter_cenario(missao)
        st.info(
            f"**Apresentação da missão:** você será responsável por organizar o {cenario['nome']}, "
            f"com orçamento inicial de {formatar_moeda(cenario['orcamento_inicial'])} e "
            f"capacidade máxima para {cenario['capacidade']} participantes. Seu objetivo é "
            "manter o equilíbrio financeiro, controlar os riscos e concluir a missão com recursos sustentáveis."
        )

        consentimento = st.checkbox(
            "Declaro que compreendi a finalidade acadêmica da ferramenta e concordo "
            "com o uso agregado e não público das respostas para avaliação do estudo."
        )
        iniciar = st.form_submit_button("▶ Iniciar missão", type="primary", width="stretch")

    if iniciar:
        if not nome.strip():
            st.error("Informe o nome ou uma identificação para iniciar a missão.")
            return
        if not consentimento:
            st.error("É necessário registrar a concordância para continuar.")
            return

        participante_id = salvar_participante(
            nome=nome, instituicao=instituicao, curso=curso, area=area, perfil=perfil,
            experiencia=experiencia, experiencia_gestao=experiencia_gestao,
        )
        tentativa = int(st.session_state.get("numero_tentativa", 1))
        simulacao_id = iniciar_simulacao(participante_id, cenario["nome"], tentativa)
        st.session_state.participante_id = participante_id
        st.session_state.simulacao_id = simulacao_id
        st.session_state.missao_selecionada = missao
        st.session_state.perfil_participante = {
            "nome": nome.strip(), "instituicao": instituicao.strip(), "curso": curso.strip(),
            "area": area, "perfil": perfil, "experiencia": experiencia,
            "experiencia_gestao": experiencia_gestao, "missao": cenario["nome"],
        }
        ir_para("diagnostico")

def pagina_diagnostico() -> None:
    cabecalho(compacto=True)
    st.title("Diagnóstico inicial")
    st.write(
        "Indique seu nível de concordância com cada afirmação. "
        "Este diagnóstico busca compreender sua percepção atual sobre gestão financeira."
    )
    st.caption("1 = Discordo totalmente · 5 = Concordo totalmente")

    with st.form("form_diagnostico"):
        respostas = {}
        for codigo, texto in QUESTOES_DIAGNOSTICO:
            respostas[codigo] = st.slider(
                texto,
                min_value=1,
                max_value=5,
                value=3,
                key=f"diag_{codigo}",
            )

        observacao = st.text_area(
            "Em poucas palavras, qual é sua principal dificuldade ao lidar com recursos financeiros em projetos?"
        )
        concluir = st.form_submit_button(
            "Concluir diagnóstico", type="primary", width='stretch'
        )

    if concluir:
        salvar_diagnostico(
            participante_id=st.session_state.participante_id,
            respostas=respostas,
            observacao=observacao,
        )
        st.session_state.diagnostico = respostas
        ir_para("cenario")



def formatar_moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def pagina_cenario() -> None:
    cabecalho(compacto=True)
    st.success("Diagnóstico registrado com sucesso.")
    st.title("Apresentação da missão")

    gestor = st.session_state.get("perfil_participante", {}).get("nome", "Gestor")
    porte = st.session_state.get("missao_selecionada", "Pequeno")
    cenario = obter_cenario(porte)
    modelos = obter_modelos_financiamento()
    propostas = obter_propostas_financiamento(porte)

    st.write(
        f"{gestor}, a missão possui recursos limitados. Escolha como formar o financiamento "
        "do evento e observe imediatamente os efeitos de sua estratégia."
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Missão", cenario["nome"])
    c2.metric("Capacidade máxima", f"{cenario['capacidade']} pessoas")
    c3.metric("Referência de recursos", formatar_moeda(cenario["orcamento_inicial"]))

    st.markdown("### Rodada 1: Escolha o modelo do evento")
    modelo = st.radio(
        "Qual estratégia principal será utilizada?",
        list(modelos.keys()),
        horizontal=True,
        key=f"modelo_fin_{porte}",
    )
    st.info(modelos[modelo]["descricao"])

    st.markdown("### Rodada 2: Defina público e fontes")
    col_publico, col_recursos = st.columns(2)
    with col_publico:
        publico_previsto = st.slider(
            "Público previsto", 0, int(cenario["capacidade"]),
            max(1, int(cenario["capacidade"] * 0.75)), 1,
            key=f"publico_{porte}",
        )
        permite_inscricao = bool(modelos[modelo]["permite_inscricao"])
        pagantes_previstos = st.slider(
            "Participantes pagantes", 0, int(publico_previsto),
            int(publico_previsto * 0.8) if permite_inscricao else 0, 1,
            disabled=not permite_inscricao, key=f"pagantes_{porte}_{modelo}",
        )
        valor_inscricao = st.number_input(
            "Valor da inscrição", min_value=0.0,
            max_value=float(cenario["valor_inscricao"] * 3),
            value=float(cenario["valor_inscricao"]) if permite_inscricao else 0.0,
            step=10.0, disabled=not permite_inscricao,
            key=f"inscricao_{porte}_{modelo}",
        )

    with col_recursos:
        usar_recurso_sugerido = st.checkbox(
            "Utilizar recurso inicial sugerido", value=True, key=f"usar_recurso_{porte}"
        )
        recurso_inicial = st.number_input(
            "Recurso inicial disponível", min_value=0.0,
            max_value=float(cenario["orcamento_inicial"] * 2),
            value=float(cenario["orcamento_inicial"]) if usar_recurso_sugerido else 0.0,
            step=500.0, disabled=usar_recurso_sugerido,
            key=f"recurso_inicial_{porte}_{usar_recurso_sugerido}",
        )
        if usar_recurso_sugerido:
            recurso_inicial = float(cenario["orcamento_inicial"])

        nomes_propostas = ["Sem apoio externo"] + list(propostas.keys())
        proposta = st.selectbox(
            "Decisão de captação", nomes_propostas, key=f"proposta_{porte}_{modelo}"
        )
        apoio_externo = 0.0 if proposta == "Sem apoio externo" else float(propostas[proposta]["valor"])
        if proposta != "Sem apoio externo":
            st.caption(
                f"Contrapartida: {propostas[proposta]['contrapartida']} "
                f"| Risco: {propostas[proposta]['risco']}/100"
            )

    receita = calcular_receita_total(
        quantidade_inscritos=int(pagantes_previstos),
        valor_inscricao=float(valor_inscricao),
        capacidade=int(cenario["capacidade"]),
        patrocinio_base=float(apoio_externo),
    )
    recursos_disponiveis = calcular_recursos_disponiveis(
        float(recurso_inicial), receita["receita_total"]
    )

    st.markdown("### Consequência imediata da decisão")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Receita com inscrições", formatar_moeda(receita["receita_inscricoes"]))
    r2.metric("Apoio externo", formatar_moeda(apoio_externo))
    r3.metric("Recurso inicial", formatar_moeda(recurso_inicial))
    r4.metric("Recursos disponíveis", formatar_moeda(recursos_disponiveis))

    avisos = []
    if recursos_disponiveis <= 0:
        avisos.append("A missão começa sem recursos. Será necessário assumir riscos elevados no planejamento.")
    if publico_previsto > 0 and pagantes_previstos > publico_previsto:
        avisos.append("O número de pagantes não pode superar o público previsto.")
    if modelo == "Evento pago" and pagantes_previstos == 0:
        avisos.append("Você escolheu um evento pago, mas não estimou participantes pagantes.")
    if modelo == "Evento gratuito patrocinado" and apoio_externo <= 0:
        avisos.append("O evento gratuito foi iniciado sem patrocínio, aumentando o risco de insuficiência financeira.")
    for aviso in avisos:
        st.warning(aviso)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Voltar ao início", width="stretch"):
            st.session_state.clear()
            st.rerun()
    with col2:
        if st.button("Confirmar estratégia e planejar", type="primary", width="stretch"):
            estrategia = {
                "modelo": modelo, "publico_previsto": int(publico_previsto),
                "pagantes_previstos": int(pagantes_previstos),
                "valor_inscricao": float(valor_inscricao),
                "recurso_inicial": float(recurso_inicial), "proposta": proposta,
                "apoio_externo": float(apoio_externo),
                "receita_inscricoes": float(receita["receita_inscricoes"]),
                "recursos_disponiveis": float(recursos_disponiveis),
                "avisos": avisos,
            }
            salvar_estrategia_financiamento(
                int(st.session_state.participante_id),
                st.session_state.get("simulacao_id"), estrategia,
            )
            st.session_state.porte_evento = porte
            st.session_state.cenario = cenario
            st.session_state.quantidade_inscritos = int(pagantes_previstos)
            st.session_state.publico_previsto = int(publico_previsto)
            st.session_state.receita = receita
            st.session_state.recursos_disponiveis = float(recursos_disponiveis)
            st.session_state.estrategia_financiamento = estrategia
            st.session_state.diario_decisoes.append({
                "etapa": "financiamento", "decisao": estrategia,
                "consequencia": {"recursos_disponiveis": recursos_disponiveis},
            })
            ir_para("planejamento")


def pagina_planejamento() -> None:
    cabecalho(compacto=True)
    st.title("Planejamento estratégico da missão")

    if "cenario" not in st.session_state:
        ir_para("cenario")
        return

    cenario = st.session_state.cenario
    porte = st.session_state.porte_evento
    recursos_disponiveis = float(st.session_state.recursos_disponiveis)
    opcoes_taticas = obter_opcoes_taticas(porte)

    exibir_conceito("orcamento")

    st.write(
        "Primeiro, distribua os recursos entre as grandes categorias. "
        "Depois, escolha uma alternativa dentro de cada categoria."
    )

    st.caption(
        f"Evento: {cenario['nome']} | "
        f"Recursos disponíveis: {formatar_moeda(recursos_disponiveis)}"
    )

    st.subheader("1. Distribuição estratégica")

    alocacoes = {}
    col1, col2 = st.columns(2)

    valor_padrao_categoria = int((recursos_disponiveis * 0.15) // 100 * 100)
    valor_padrao_reserva = int((recursos_disponiveis * 0.10) // 100 * 100)

    for i, categoria in enumerate(CATEGORIAS):
        coluna = col1 if i % 2 == 0 else col2
        valor_padrao = (
            valor_padrao_reserva
            if categoria == "Reserva de contingência"
            else valor_padrao_categoria
        )

        with coluna:
            alocacoes[categoria] = st.number_input(
                categoria,
                min_value=0,
                max_value=int(recursos_disponiveis),
                value=valor_padrao,
                step=100,
                key=f"alocacao_{porte}_{categoria}",
            )

    saldo = calcular_saldo_planejamento(
        alocacoes,
        recursos_disponiveis,
    )
    total_alocado = recursos_disponiveis - saldo

    m1, m2, m3 = st.columns(3)
    m1.metric("Recursos disponíveis", formatar_moeda(recursos_disponiveis))
    m2.metric("Total distribuído", formatar_moeda(total_alocado))
    m3.metric("Saldo não distribuído", formatar_moeda(saldo))

    valido, mensagem = validar_alocacoes(
        alocacoes,
        recursos_disponiveis,
    )
    riscos_alocacao = analisar_riscos_alocacoes(
        alocacoes,
        recursos_disponiveis,
    )

    if riscos_alocacao:
        st.warning(
            "O sistema identificou riscos, mas não impedirá a continuidade."
        )
        for aviso in riscos_alocacao:
            st.write(f"• {aviso}")
    else:
        st.success(mensagem)

    st.divider()
    st.subheader("2. Escolhas táticas")

    escolhas = {}

    for categoria, opcoes in opcoes_taticas.items():
        st.markdown(f"#### {categoria}")

        escolha_nome = st.radio(
            f"Selecione a alternativa para {categoria}",
            list(opcoes.keys()),
            horizontal=True,
            key=f"escolha_{porte}_{categoria}",
        )

        escolha = opcoes[escolha_nome]
        escolhas[categoria] = {"opcao": escolha_nome, **escolha}

        c1, c2, c3 = st.columns([1, 1, 2])
        c1.metric("Custo", formatar_moeda(escolha["custo"]))
        c2.metric("Qualidade", f"{escolha['qualidade']}/100")
        c3.write(escolha["descricao"])

        limite = alocacoes.get(categoria, 0)

        if escolha["custo"] > limite:
            st.warning(
                f"A alternativa selecionada custa "
                f"{formatar_moeda(escolha['custo'])}, mas você destinou "
                f"{formatar_moeda(limite)} à categoria."
            )

    valido_tatico, mensagem_tatica = validar_escolhas_taticas(
        alocacoes,
        escolhas,
    )
    riscos_taticos = analisar_riscos_escolhas_taticas(
        alocacoes,
        escolhas,
    )

    if riscos_taticos:
        st.warning(mensagem_tatica)
        for aviso in riscos_taticos:
            st.write(f"• {aviso}")
    else:
        st.success(mensagem_tatica)

    st.divider()
    st.subheader("Resumo do planejamento")

    resumo = calcular_resumo_planejamento(
        alocacoes,
        escolhas,
        recursos_disponiveis,
    )

    resumo.update(
        {
            "porte_evento": porte,
            "nome_evento": cenario["nome"],
            "orcamento_inicial": st.session_state.estrategia_financiamento["recurso_inicial"],
            "quantidade_inscritos": st.session_state.quantidade_inscritos,
            "publico_previsto": st.session_state.get("publico_previsto", st.session_state.quantidade_inscritos),
            "modelo_financiamento": st.session_state.estrategia_financiamento.get("modelo", ""),
            "proposta_financiamento": st.session_state.estrategia_financiamento.get("proposta", ""),
            "valor_inscricao": st.session_state.estrategia_financiamento["valor_inscricao"],
            "receita_inscricoes": st.session_state.receita["receita_inscricoes"],
            "patrocinio": st.session_state.receita["patrocinio_total"],
            "receita_total": st.session_state.receita["receita_total"],
            "recursos_disponiveis": recursos_disponiveis,
        }
    )

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Custo das escolhas", formatar_moeda(resumo["custo_escolhas"]))
    r2.metric("Reserva", formatar_moeda(resumo["reserva"]))
    r3.metric("Reserva (%)", f"{resumo['percentual_reserva']:.1f}%")
    r4.metric(
        "Saldo não comprometido",
        formatar_moeda(resumo["saldo_nao_comprometido"]),
    )

    if st.button(
        "Confirmar planejamento",
        type="primary",
        width='stretch',
        disabled=False,
    ):
        avisos_planejamento = riscos_alocacao + riscos_taticos
        resumo["avisos_risco"] = avisos_planejamento
        resumo["quantidade_avisos"] = len(avisos_planejamento)

        salvar_planejamento(
            st.session_state.participante_id,
            alocacoes,
            escolhas,
            resumo,
        )

        st.session_state.alocacoes = alocacoes
        st.session_state.escolhas_taticas = escolhas
        st.session_state.resumo_planejamento = resumo
        st.session_state.avisos_planejamento = avisos_planejamento
        motor = criar_motor_financeiro(
            orcamento_inicial=resumo["orcamento_inicial"],
            receita_inscricoes=resumo["receita_inscricoes"],
            patrocinio=resumo["patrocinio"],
        )
        motor["modelo_financiamento"] = resumo.get("modelo_financiamento", "")
        motor["proposta_financiamento"] = resumo.get("proposta_financiamento", "")
        motor["publico_previsto"] = resumo.get("publico_previsto", 0)
        motor["quantidade_inscritos"] = resumo.get("quantidade_inscritos", 0)
        motor["valor_inscricao"] = resumo.get("valor_inscricao", 0)
        resumo_motor = registrar_planejamento(
            motor,
            escolhas=escolhas,
            reserva_planejada=resumo["reserva"],
        )
        st.session_state.motor_financeiro = motor

        st.session_state.diario_decisoes.append(
            {
                "etapa": "planejamento",
                "alocacoes": dict(alocacoes),
                "escolhas": dict(escolhas),
                "avisos": list(avisos_planejamento),
                "resultado_projetado": {
                    "custo_escolhas": resumo["custo_escolhas"],
                    "reserva": resumo["reserva"],
                    "saldo_nao_comprometido": resumo["saldo_nao_comprometido"],
                },
                "impacto_financeiro": resumo_motor,
            }
        )
        st.session_state.eventos_sorteados = sortear_eventos(
            3, st.session_state.get("historico_eventos_ids", [])
        )
        st.session_state.historico_eventos_ids = [
            evento["id"] for evento in st.session_state.eventos_sorteados
        ]
        st.session_state.indice_evento = 0
        st.session_state.decisoes_eventos = []
        st.session_state.rolar_topo_evento = True

        ir_para("evento")


def pagina_evento() -> None:
    cabecalho(compacto=True)
    st.title("Eventos inesperados")

    if st.session_state.pop("rolar_topo_evento", False):
        rolar_para_topo()

    if "eventos_sorteados" not in st.session_state:
        st.session_state.eventos_sorteados = sortear_eventos(
            3, st.session_state.get("historico_eventos_ids", [])
        )
        st.session_state.historico_eventos_ids = [
            evento["id"] for evento in st.session_state.eventos_sorteados
        ]
        st.session_state.indice_evento = 0
        st.session_state.decisoes_eventos = []

    eventos = st.session_state.eventos_sorteados
    indice = st.session_state.indice_evento
    evento = obter_evento(eventos, indice)

    if evento is None:
        ir_para("planejamento_concluido")
        return

    total_eventos = len(eventos)

    st.progress((indice + 1) / total_eventos)
    st.caption(f"Evento inesperado {indice + 1} de {total_eventos}")
    st.subheader(evento["titulo"])
    st.info(evento["descricao"])

    opcoes = evento["opcoes"]
    textos_opcoes = [opcao["texto"] for opcao in opcoes]

    escolha_texto = st.radio(
        "Como você deseja responder a esta situação?",
        textos_opcoes,
        index=None,
        key=f"evento_{evento['id']}_opcao",
        help="Leia a descrição do imprevisto e selecione conscientemente uma alternativa.",
    )

    if escolha_texto is None:
        st.info(
            "Leia a descrição do imprevisto acima e selecione uma alternativa para "
            "visualizar seus impactos antes de confirmar a decisão."
        )
        return

    escolha = next(
        opcao for opcao in opcoes
        if opcao["texto"] == escolha_texto
    )

    st.markdown("### Impactos da decisão")
    evento_cancelamento = evento.get("tipo_evento") == "cancelamento_inscricoes"
    valor_reembolso_estimado = 0.0
    valor_baixa_estimado = 0.0
    if evento_cancelamento:
        motor_atual = st.session_state.get("motor_financeiro", {})
        recebido_base = float(motor_atual.get("inscricoes_recebidas_inicial", 0.0))
        a_receber_base = float(motor_atual.get("inscricoes_a_receber_inicial", 0.0))
        valor_reembolso_estimado = recebido_base * float(
            escolha.get("percentual_reembolso_recebido", 0.0)
        )
        valor_baixa_estimado = a_receber_base * float(
            escolha.get("percentual_baixa_a_receber", 0.0)
        )
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Reembolso pelo banco", formatar_moeda(valor_reembolso_estimado))
        c2.metric("Baixa em contas a receber", formatar_moeda(valor_baixa_estimado))
        c3.metric("Nível de risco", f"{escolha['risco']}/100")
        c4.metric("Qualidade esperada", f"{escolha['qualidade']}/100")
        st.caption(
            "O reembolso reduz o saldo bancário. A baixa reduz o Contas a Receber. "
            "Ambos reduzem a receita líquida do projeto."
        )
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Custo adicional", formatar_moeda(escolha["custo"]))
        c2.metric("Nível de risco", f"{escolha['risco']}/100")
        c3.metric("Qualidade esperada", f"{escolha['qualidade']}/100")

    saldo_planejamento = float(
        st.session_state.resumo_planejamento["saldo_nao_comprometido"]
    )

    custo_eventos_anteriores = sum(
        decisao["custo"]
        for decisao in st.session_state.decisoes_eventos
    )

    saldo_antes_decisao = saldo_planejamento - custo_eventos_anteriores
    impacto_bancario_decisao = (
        valor_reembolso_estimado if evento_cancelamento else float(escolha["custo"])
    )
    saldo_depois_decisao = saldo_antes_decisao - impacto_bancario_decisao

    st.markdown("### Situação financeira")
    s1, s2 = st.columns(2)
    s1.metric(
        "Saldo antes da decisão",
        formatar_moeda(saldo_antes_decisao),
    )
    s2.metric(
        "Saldo após a decisão",
        formatar_moeda(saldo_depois_decisao),
        delta=formatar_moeda(-impacto_bancario_decisao),
    )

    if saldo_depois_decisao < 0:
        st.warning(
            "Esta decisão fará com que o projeto fique com saldo financeiro negativo."
        )

    if st.button(
        "Confirmar decisão",
        type="primary",
        width='stretch',
    ):
        decisao = {
            "evento_id": evento["id"],
            "tipo_evento": evento.get("tipo_evento", "evento_operacional"),
            "titulo": evento["titulo"],
            "opcao": escolha["texto"],
            "custo": escolha["custo"],
            "risco": escolha["risco"],
            "qualidade": escolha["qualidade"],
            "percentual_reembolso_recebido": escolha.get(
                "percentual_reembolso_recebido", 0.0
            ),
            "percentual_baixa_a_receber": escolha.get(
                "percentual_baixa_a_receber", 0.0
            ),
        }

        salvar_evento(
            participante_id=st.session_state.participante_id,
            evento_id=evento["id"],
            titulo=evento["titulo"],
            opcao=escolha["texto"],
            custo=escolha["custo"],
            risco=escolha["risco"],
            qualidade=escolha["qualidade"],
        )

        st.session_state.decisoes_eventos.append(decisao)
        if st.session_state.get("motor_financeiro"):
            impacto_evento = registrar_evento_financeiro(
                st.session_state.motor_financeiro,
                decisao,
            )
            st.session_state.diario_decisoes.append(
                {
                    "etapa": "evento",
                    "decisao": dict(decisao),
                    "impacto_financeiro": impacto_evento,
                }
            )
        st.session_state.indice_evento += 1

        if st.session_state.indice_evento >= total_eventos:
            ir_para("planejamento_concluido")
        else:
            st.session_state.rolar_topo_evento = True
            st.rerun()


def _tabela_monetaria(linhas: list[dict]) -> None:
    st.dataframe(
        linhas,
        width="stretch",
        hide_index=True,
        column_config={
            "Valor": st.column_config.NumberColumn(format="R$ %.2f"),
            "Entrada": st.column_config.NumberColumn(format="R$ %.2f"),
            "Saída": st.column_config.NumberColumn(format="R$ %.2f"),
            "Saldo": st.column_config.NumberColumn(format="R$ %.2f"),
        },
    )


def _exibir_observacoes(titulo: str, observacoes: list[str]) -> None:
    st.markdown(f"**{titulo}**")
    for texto in observacoes:
        st.markdown(f"- {texto}")


def _exibir_dashboard_financeiro(motor: dict, resumo: dict, dre: dict, balanco: dict) -> None:
    st.subheader("Dashboard Financeiro")
    st.caption("Visão executiva dos resultados econômicos e financeiros da tentativa.")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Receita líquida", formatar_moeda(dre["receita_liquida"]))
    k2.metric("Despesas totais", formatar_moeda(dre["custos_diretos"] + dre["despesas_operacionais"]))
    k3.metric("Lucro líquido", formatar_moeda(dre["lucro_liquido"]))
    k4.metric("Caixa livre após reserva", formatar_moeda(resumo["caixa_livre_apos_reserva"]))

    col1, col2 = st.columns(2)
    with col1:
        comparativo = pd.DataFrame({
            "Grupo": ["Receita líquida", "Custos e despesas", "Lucro líquido"],
            "Valor": [
                dre["receita_liquida"],
                dre["custos_diretos"] + dre["despesas_operacionais"],
                dre["lucro_liquido"],
            ],
        })
        fig = px.bar(comparativo, x="Grupo", y="Valor", text_auto=".2s", title="Receita, gastos e resultado")
        fig.update_layout(yaxis_title="Valor (R$)", xaxis_title="", showlegend=False)
        st.plotly_chart(
            fig,
            width="stretch",
            config={"staticPlot": True, "displayModeBar": False},
        )

    with col2:
        gastos = {}
        for item in motor.get("lancamentos", []):
            if item.get("natureza_dre") == "despesa_operacional":
                categoria = str(item.get("categoria", "Outros"))
                gastos[categoria] = gastos.get(categoria, 0.0) + float(item.get("valor", 0.0))
        if gastos:
            df_gastos = pd.DataFrame({"Categoria": list(gastos), "Valor": list(gastos.values())})
            fig = px.pie(df_gastos, names="Categoria", values="Valor", hole=0.45, title="Distribuição dos gastos")
            st.plotly_chart(
            fig,
            width="stretch",
            config={"staticPlot": True, "displayModeBar": False},
        )
        else:
            st.info("Não existem despesas registradas para compor o gráfico.")

    fluxo = calcular_fluxo_caixa(motor)
    if fluxo:
        df_fluxo = pd.DataFrame({
            "Etapa": [f"{i+1}. {item['fase']}" for i, item in enumerate(fluxo)],
            "Saldo": [item["saldo"] for item in fluxo],
            "Descrição": [item["descricao"] for item in fluxo],
        })
        fig = px.line(df_fluxo, x="Etapa", y="Saldo", markers=True, hover_data=["Descrição"], title="Evolução do saldo bancário")
        fig.add_hline(y=0, line_dash="dash")
        fig.update_layout(xaxis_title="Movimentações", yaxis_title="Saldo (R$)")
        st.plotly_chart(
            fig,
            width="stretch",
            config={"staticPlot": True, "displayModeBar": False},
        )

    col3, col4 = st.columns(2)
    with col3:
        composicao_ativo = pd.DataFrame({
            "Conta": ["Banco Conta Movimento", "Contas a Receber"],
            "Valor": [
                next((x["Valor"] for x in balanco.get("ativo", []) if "Banco" in x.get("Conta", "")), 0.0),
                next((x["Valor"] for x in balanco.get("ativo", []) if "receber" in x.get("Conta", "").lower()), 0.0),
            ],
        })
        composicao_ativo = composicao_ativo[composicao_ativo["Valor"] != 0]
        if not composicao_ativo.empty:
            fig = px.bar(composicao_ativo, x="Conta", y="Valor", title="Composição do Ativo")
            fig.update_layout(xaxis_title="", yaxis_title="Valor (R$)", showlegend=False)
            st.plotly_chart(
            fig,
            width="stretch",
            config={"staticPlot": True, "displayModeBar": False},
        )
    with col4:
        margem = (dre["lucro_liquido"] / dre["receita_liquida"] * 100) if dre["receita_liquida"] else 0.0
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=margem,
            number={"suffix": "%"},
            title={"text": "Margem líquida"},
            gauge={"axis": {"range": [-100, 100]}, "threshold": {"line": {"width": 4}, "value": 0}},
        ))
        fig.update_layout(height=330)
        st.plotly_chart(
            fig,
            width="stretch",
            config={"staticPlot": True, "displayModeBar": False},
        )


def pagina_planejamento_concluido() -> None:
    cabecalho(compacto=True)
    st.success(f"Missão concluída, {st.session_state.get('perfil_participante', {}).get('nome', 'gestor')}!")
    st.title("Missão concluída: resultados financeiros")
    st.info(
        "Nesta versão, 80% da receita de inscrições é considerada recebida no Banco "
        "Conta Movimento e 20% permanece inicialmente em Contas a Receber. Essa "
        "separação permite comparar resultado econômico e disponibilidade financeira."
    )

    motor = st.session_state.get("motor_financeiro", {})
    if not motor:
        st.error("Não foi possível localizar os lançamentos financeiros da simulação.")
        return

    resumo_motor = atualizar_resumo(motor)
    dre = calcular_dre_analitica(motor)
    balanco = calcular_balanco_analitico(motor)
    analises = analisar_resultados_financeiros(motor)
    indicadores = calcular_indicadores_analiticos(motor)

    simulacao_id = st.session_state.get("simulacao_id")
    if simulacao_id and not st.session_state.get("simulacao_finalizada"):
        finalizar_simulacao(
            int(simulacao_id),
            lucro=float(dre.get("lucro_liquido", 0.0)),
            saldo_caixa=float(resumo_motor.get("saldo_caixa", 0.0)),
            resultado={
                "missao": st.session_state.get("perfil_participante", {}).get("missao"),
                "tentativa": int(st.session_state.get("numero_tentativa", 1)),
                "indicadores": indicadores,
            },
        )
        st.session_state.simulacao_finalizada = True

    _exibir_dashboard_financeiro(motor, resumo_motor, dre, balanco)

    st.divider()
    st.subheader("Relatórios Financeiros Detalhados")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Entradas no banco", formatar_moeda(resumo_motor["entradas_caixa"]))
    c2.metric("Saídas do banco", formatar_moeda(resumo_motor["saidas_caixa"]))
    c3.metric("Saldo bancário", formatar_moeda(resumo_motor["saldo_caixa"]))
    c4.metric("Lucro líquido", formatar_moeda(dre["lucro_liquido"]))

    if resumo_motor["caixa_livre_apos_reserva"] < 0:
        st.warning(
            "O saldo bancário não é suficiente para preservar integralmente a "
            "reserva planejada. Essa situação será considerada na reflexão pedagógica."
        )
    else:
        st.success(
            f"Após preservar a reserva de {formatar_moeda(resumo_motor['reserva_planejada'])}, "
            f"o projeto mantém {formatar_moeda(resumo_motor['caixa_livre_apos_reserva'])} livres."
        )

    st.divider()
    exibir_conceito("fluxo_caixa")
    st.subheader("Fluxo de Caixa do Projeto (analítico)")
    fluxo = calcular_fluxo_caixa(motor)
    tabela_fluxo = [
        {
            "Fase": linha["fase"],
            "Descrição": linha["descricao"],
            "Entrada": linha["entrada"],
            "Saída": linha["saida"],
            "Saldo": linha["saldo"],
        }
        for linha in fluxo
    ]
    _tabela_monetaria(tabela_fluxo)
    st.markdown("**Como interpretar?**")
    st.write(
        "Acompanhe a sequência das entradas e saídas no Banco Conta Movimento e observe o saldo após cada "
        "movimentação. Um saldo negativo indica que, naquele momento, os recursos "
        "disponíveis não seriam suficientes para cumprir os pagamentos."
    )
    _exibir_observacoes("Análise desta simulação", analises["fluxo"])

    st.divider()
    exibir_conceito("dre")
    st.subheader("Demonstração do Resultado do Projeto (analítica)")
    if dre["linhas"]:
        _tabela_monetaria(dre["linhas"])
    else:
        st.info("Não existem lançamentos operacionais para compor a demonstração.")

    resumo_dre = [
        {"Descrição": "(+) Receita Bruta do Evento", "Valor": dre["receita_bruta"]},
        {"Descrição": "(-) Deduções da Receita Bruta", "Valor": dre["deducoes"]},
        {"Descrição": "(=) Receita Líquida do Evento", "Valor": dre["receita_liquida"]},
        {"Descrição": "(-) Custos Diretos do Evento", "Valor": dre["custos_diretos"]},
        {"Descrição": "(=) Lucro Bruto do Evento", "Valor": dre["lucro_bruto"]},
        {"Descrição": "(-) Despesas Operacionais", "Valor": dre["despesas_operacionais"]},
        {"Descrição": "(=) Resultado Operacional (EBIT)", "Valor": dre["resultado_operacional"]},
        {"Descrição": "(+/-) Resultado Financeiro", "Valor": dre["resultado_financeiro"]},
        {"Descrição": "(=) Resultado Antes dos Tributos", "Valor": dre["lair"]},
        {"Descrição": "(-) Tributos sobre o Lucro", "Valor": dre["tributos_lucro"]},
        {"Descrição": "(=) Lucro Líquido do Evento", "Valor": dre["lucro_liquido"]},
    ]
    _tabela_monetaria(resumo_dre)
    st.caption(
        "O capital inicial é aporte do projeto e não integra a receita da DRE. "
        "Deduções, resultado financeiro e tributos permanecem zerados quando não "
        "há decisões específicas que os originem."
    )
    st.markdown("**Como interpretar?**")
    st.write(
        "A DRE evidencia a formação do resultado. Primeiro são identificadas as "
        "receitas; depois, os custos diretamente ligados ao evento e as despesas "
        "operacionais. Resultado positivo representa lucro; resultado negativo, prejuízo."
    )
    _exibir_observacoes("Análise desta simulação", analises["dre"])

    st.divider()
    exibir_conceito("balanco")
    st.subheader("Balanço Patrimonial Simplificado do Projeto (analítico)")
    exibir_titulo_com_ajuda("Ativo", TERMOS_EDUCACIONAIS["ativo"])
    _tabela_monetaria(balanco["ativo"])
    st.metric("Total do Ativo", formatar_moeda(balanco["total_ativo"]))

    exibir_titulo_com_ajuda("Passivo", TERMOS_EDUCACIONAIS["passivo"])
    _tabela_monetaria(balanco["passivo"])
    st.metric("Total do Passivo", formatar_moeda(balanco["total_passivo"]))

    exibir_titulo_com_ajuda(
        "Patrimônio Líquido",
        TERMOS_EDUCACIONAIS["patrimonio_liquido"],
    )
    _tabela_monetaria(balanco["patrimonio"])
    p1, p2 = st.columns(2)
    p1.metric("Total do Patrimônio Líquido", formatar_moeda(balanco["total_patrimonio"]))
    p2.metric(
        "Total do Passivo + Patrimônio Líquido",
        formatar_moeda(balanco["total_passivo_pl"]),
    )
    st.caption(
        "O modelo é simplificado e utiliza apenas contas efetivamente representadas "
        "na simulação. O capital inicial e os recebimentos são movimentados no Banco "
        "Conta Movimento; as inscrições pendentes permanecem em Contas a Receber."
    )
    st.markdown("**Como interpretar?**")
    st.write(
        "O Ativo mostra onde os recursos estão aplicados, incluindo o saldo bancário "
        "e as inscrições a receber. O Passivo demonstra obrigações ou necessidades "
        "de financiamento. O Patrimônio Líquido reúne "
        "o capital inicial e o resultado acumulado do projeto."
    )
    _exibir_observacoes("Análise desta simulação", analises["balanco"])

    st.divider()
    exibir_conceito("indicadores")
    st.subheader("Indicadores Financeiros do Projeto (analíticos)")
    st.caption(
        "Os indicadores utilizam somente valores efetivamente registrados na simulação. "
        "Quando a base de cálculo é zero ou não existe passivo, o resultado é apresentado "
        "como não aplicável, evitando interpretações artificiais."
    )

    for indicador in indicadores["linhas"]:
        with st.container(border=True):
            c_ind, c_res = st.columns([3, 1])
            with c_ind:
                if "(ROI)" in indicador["Indicador"]:
                    exibir_titulo_com_ajuda(
                        indicador["Indicador"],
                        TERMOS_EDUCACIONAIS["roi"],
                        nivel="###",
                    )
                elif indicador["Indicador"].strip().lower() == "margem líquida":
                    exibir_titulo_com_ajuda(
                        indicador["Indicador"],
                        TERMOS_EDUCACIONAIS["margem_liquida"],
                        nivel="###",
                    )
                else:
                    st.markdown(f"### {indicador['Indicador']}")
                st.markdown(f"**Fórmula:** {indicador['Fórmula']}")
                st.markdown(f"**Memória de cálculo:** {indicador['Memória de cálculo']}")
            with c_res:
                resultado = indicador["Resultado"]
                if resultado is None:
                    st.metric("Resultado", "Não aplicável")
                elif indicador["Unidade"] == "%":
                    st.metric("Resultado", f"{resultado:.2f}%")
                else:
                    st.metric("Resultado", f"{resultado:.2f}")

    st.markdown("**Como interpretar?**")
    st.write(
        "Analise os indicadores em conjunto. Rentabilidade positiva não elimina riscos "
        "de caixa, concentração de gastos ou dependência excessiva de uma única receita. "
        "Indicadores não aplicáveis também são informativos, pois demonstram que não houve "
        "base contábil para o cálculo naquele cenário."
    )
    _exibir_observacoes("Análise desta simulação", indicadores["observacoes"])

    motor["indicadores"] = indicadores

    st.divider()
    st.subheader("Reflexão final da missão")
    feedback = gerar_feedback_aprendizagem(
        motor, resumo_motor, dre, indicadores
    )
    st.info(feedback["mensagem"])

    st.markdown("### Resultado")
    for item in feedback["fatos"]:
        st.markdown(f"- {item}")

    col_acertos, col_atencao = st.columns(2)
    with col_acertos:
        st.markdown("### O que contribuiu positivamente")
        for item in feedback["acertos"]:
            st.markdown(f"- ✅ {item}")
    with col_atencao:
        st.markdown("### Pontos de atenção")
        for item in feedback["atencao"]:
            st.markdown(f"- ⚠️ {item}")

    st.markdown("### O que fazer na próxima tentativa")
    for item in feedback["recomendacoes"]:
        st.markdown(f"- {item}")

    st.divider()
    st.subheader("🤖 Tutor Inteligente")
    st.caption(
        "A inteligência artificial não realiza os cálculos financeiros. Ela recebe "
        "somente os resultados já apurados pelo motor determinístico e os transforma "
        "em uma orientação pedagógica personalizada."
    )

    if tutor_disponivel():
        if st.button(
            "Gerar orientação do Tutor Inteligente",
            type="secondary",
            width="stretch",
        ):
            with st.spinner("O Tutor Inteligente está analisando a tentativa..."):
                try:
                    st.session_state.feedback_tutor_ia = gerar_feedback_tutor_ia(
                        motor, resumo_motor, dre, indicadores, feedback
                    )
                except Exception as erro:
                    st.session_state.feedback_tutor_ia = ""
                    st.session_state.erro_tutor_ia = mensagem_amigavel_erro_tutor(erro)
                else:
                    st.session_state.erro_tutor_ia = ""

        if st.session_state.get("feedback_tutor_ia"):
            with st.container(border=True):
                st.markdown(st.session_state.feedback_tutor_ia)
            st.caption(
                "Conteúdo gerado por IA a partir dos resultados da simulação. "
                "A análise deve ser utilizada como apoio à reflexão."
            )
        elif st.session_state.get("erro_tutor_ia"):
            st.warning(st.session_state.erro_tutor_ia)
            with st.container(border=True):
                st.markdown(montar_feedback_contingencia(feedback))
    else:
        st.warning(
            "Tutor Inteligente não configurado. A análise pedagógica baseada em regras "
            "continua disponível normalmente."
        )
        with st.container(border=True):
            st.markdown(montar_feedback_contingencia(feedback))
        with st.expander("Como configurar o Tutor Inteligente"):
            st.code(
                'OPENAI_API_KEY = "sua_chave_aqui"\n'
                'OPENAI_MODEL = "gpt-5-mini"',
                language="toml",
            )
            st.write(
                "A chave permanece no computador e não é exibida aos participantes."
            )

    st.divider()
    st.subheader("Relatório da Missão")
    st.caption(
        "O arquivo reúne identificação, decisões, demonstrações financeiras, indicadores, "
        "reflexão pedagógica e, quando já gerada, a orientação do Tutor Inteligente."
    )
    relatorio_html = gerar_relatorio_html(
        perfil=st.session_state.get("perfil_participante", {}),
        tentativa=int(st.session_state.get("numero_tentativa", 1)),
        resumo=resumo_motor,
        fluxo=fluxo,
        dre=dre,
        balanco=balanco,
        indicadores=indicadores,
        feedback=feedback,
        decisoes_eventos=st.session_state.get("decisoes_eventos", []),
        tutor_ia=st.session_state.get("feedback_tutor_ia", ""),
    )
    st.download_button(
        "Baixar relatório para imprimir ou salvar em PDF",
        data=relatorio_html,
        file_name=f"STEM_FinanceLab_missao_tentativa_{st.session_state.get('numero_tentativa', 1)}.html",
        mime="text/html",
        type="primary",
        width="stretch",
    )
    st.info(
        "Para imprimir: baixe o relatório, abra o arquivo no navegador e use a opção "
        "Imprimir. No celular, escolha Compartilhar ou Menu e depois Imprimir; também "
        "é possível selecionar Salvar como PDF."
    )

    st.caption(
        f"Tentativa concluída: {st.session_state.get('numero_tentativa', 1)}. "
        "Você pode testar outra estratégia ou encerrar sua participação."
    )

    st.markdown("### O que deseja fazer agora?")
    col_nova, col_encerrar = st.columns(2)

    with col_nova:
        if st.button("🔄 Jogar novamente", type="primary", width="stretch"):
            participante_id = st.session_state.get("participante_id")
            perfil_participante = dict(st.session_state.get("perfil_participante", {}))
            diagnostico = dict(st.session_state.get("diagnostico", {}))
            historico_eventos = list(st.session_state.get("historico_eventos_ids", []))
            missao_selecionada = st.session_state.get("missao_selecionada", "Pequeno")
            proxima_tentativa = int(st.session_state.get("numero_tentativa", 1)) + 1
            nova_simulacao_id = iniciar_simulacao(
                int(participante_id),
                obter_cenario(missao_selecionada)["nome"],
                proxima_tentativa,
            )

            st.session_state.clear()
            st.session_state.participante_id = participante_id
            st.session_state.simulacao_id = nova_simulacao_id
            st.session_state.missao_selecionada = missao_selecionada
            st.session_state.perfil_participante = perfil_participante
            st.session_state.diagnostico = diagnostico
            st.session_state.historico_eventos_ids = historico_eventos
            st.session_state.numero_tentativa = proxima_tentativa
            st.session_state.simulacao_finalizada = False
            st.session_state.etapa = "cenario"
            st.rerun()

    with col_encerrar:
        if st.button("🚪 Encerrar sessão", width="stretch"):
            encerrar_para_agradecimento("concluida")


def pagina_agradecimento() -> None:
    cabecalho()
    nome = st.session_state.get("nome_agradecimento", "Participante")
    motivo = st.session_state.get("motivo_encerramento", "concluida")

    st.markdown("## Obrigado pela sua participação!")
    if motivo == "interrompida":
        st.info(
            f"{nome}, sua sessão foi encerrada e a tentativa foi registrada como interrompida."
        )
    else:
        st.success(
            f"{nome}, sua participação foi concluída e os resultados da missão foram registrados com sucesso."
        )

    st.write(
        "Esperamos que a experiência tenha contribuído para o desenvolvimento dos seus "
        "conhecimentos em gestão financeira."
    )
    st.caption(
        "O STEM FinanceLab é um artefato desenvolvido no âmbito de um Mestrado Profissional."
    )

    if st.button("Voltar à página inicial", type="primary", width="stretch"):
        st.session_state.clear()
        st.session_state.etapa = "inicio"
        st.rerun()



etapa = st.session_state.get("etapa", "inicio")

if etapa in {"diagnostico", "cenario", "planejamento", "evento"}:
    controle_encerramento_durante_missao()

if etapa == "inicio":
    pagina_inicial()

elif etapa == "diagnostico":
    if not st.session_state.participante_id:
        ir_para("inicio")
    pagina_diagnostico()

elif etapa == "cenario":
    if not st.session_state.participante_id:
        ir_para("inicio")
    pagina_cenario()

elif etapa == "planejamento":
    if not st.session_state.participante_id:
        ir_para("inicio")
    pagina_planejamento()

elif etapa == "evento":
    if not st.session_state.participante_id:
        ir_para("inicio")

    if "resumo_planejamento" not in st.session_state:
        ir_para("cenario")

    pagina_evento()

elif etapa == "planejamento_concluido":
    if not st.session_state.participante_id:
        ir_para("inicio")
    pagina_planejamento_concluido()

elif etapa == "agradecimento":
    pagina_agradecimento()

else:
    ir_para("inicio")

rodape()
