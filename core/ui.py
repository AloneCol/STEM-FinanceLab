import streamlit as st

from core.config import APP_VERSION


def aplicar_estilo() -> None:
    st.markdown(
        """
        <style>
            .block-container {
                max-width: 1150px;
                padding-top: 2rem;
                padding-bottom: 3rem;
            }

            .hero {
                padding: 2rem;
                border: 1px solid rgba(128,128,128,.25);
                border-radius: 18px;
                text-align: center;
                margin-bottom: 1rem;
            }

            .hero h1 {
                font-size: 2.7rem;
                margin-bottom: .2rem;
            }

            .hero p {
                font-size: 1.15rem;
                margin: 0;
                opacity: .8;
            }

            .hero-subtitle {
                text-align: center;
                font-size: 1.2rem;
                margin: 1rem 0 1.5rem 0;
            }

            .info-card {
                border: 1px solid rgba(128,128,128,.25);
                border-radius: 14px;
                padding: 1.25rem;
                margin-bottom: 1rem;
                min-height: 100%;
            }

            .info-card h3 {
                margin-top: 0;
            }

            .footer {
                text-align: center;
                opacity: .65;
                font-size: .85rem;
                margin-top: 3rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def cabecalho(compacto: bool = False) -> None:
    if compacto:
        st.markdown("## 📊 STEM FinanceLab")
        st.caption("Jogo Estratégico de Gerenciamento de Recursos para o Ensino de Princípios Financeiros a Profissionais STEM")
        st.divider()
    else:
        st.markdown(
            """
            <div class="hero">
                <h1>📊 STEM FinanceLab</h1>
                <p>Jogo Estratégico de Gerenciamento de Recursos para o Ensino de Princípios Financeiros a Profissionais STEM</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def rodape() -> None:
    st.markdown(
        f"""
        <div class="footer">
            STEM FinanceLab · Versão {APP_VERSION} · Serious Game para Educação Financeira · 2026
        </div>
        """,
        unsafe_allow_html=True,
    )
