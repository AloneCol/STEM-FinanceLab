import streamlit as st

from core.config import APP_VERSION

VERDE = "#2f9e41"
VERMELHO = "#cd191e"
SUBTITULO = (
    "Simulador Educacional Gamificado para o Ensino de Planejamento e "
    "Controle Financeiro a Estudantes e Profissionais STEM"
)

ESTILO = """
<style>
    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 0 0 1rem 0;
        border-bottom: 3px solid __VERDE__;
        text-align: left;
        margin-bottom: 1.25rem;
    }

    .hero h1 {
        font-size: 2.3rem;
        margin-bottom: .25rem;
    }

    .hero p {
        font-size: 1.05rem;
        margin: 0;
        opacity: .8;
    }

    .hero-subtitle {
        text-align: left;
        font-size: 1.1rem;
        margin: 0 0 1.5rem 0;
    }

    .info-card {
        border-left: 4px solid __VERDE__;
        background: rgba(47, 158, 65, .06);
        border-radius: 4px;
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
        min-height: 100%;
    }

    .info-card h3 {
        margin-top: 0;
        font-size: 1.15rem;
    }

    .footer {
        text-align: center;
        opacity: .75;
        font-size: .85rem;
        margin-top: 3rem;
        padding-top: .75rem;
        border-top: 2px solid __VERMELHO__;
    }
</style>
""".replace("__VERDE__", VERDE).replace("__VERMELHO__", VERMELHO)


def aplicar_estilo() -> None:
    st.markdown(ESTILO, unsafe_allow_html=True)


def cabecalho(compacto: bool = False) -> None:
    if compacto:
        st.markdown("## STEM FinanceLab")
        st.caption(SUBTITULO)
        st.divider()
    else:
        st.markdown(
            f"""
            <div class="hero">
                <h1>STEM FinanceLab</h1>
                <p>{SUBTITULO}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def rodape() -> None:
    st.markdown(
        f"""
        <div class="footer">
            STEM FinanceLab · Versão {APP_VERSION} · Dissertação de mestrado, PPCOMP/Ifes ·
            Ricardo Souza de Oliveira · 2026
        </div>
        """,
        unsafe_allow_html=True,
    )
