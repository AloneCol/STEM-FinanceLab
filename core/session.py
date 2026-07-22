import streamlit as st


def inicializar_sessao() -> None:
    valores_padrao = {
        "etapa": "inicio",
        "participante_id": None,
        "simulacao_id": None,
        "missao_selecionada": "Pequeno",
        "perfil_participante": {},
        "diagnostico": {},
        "alocacoes": {},
        "escolhas_taticas": {},
        "resumo_planejamento": {},
        "diario_decisoes": [],
        "avisos_planejamento": [],
        "motor_financeiro": {},
        "historico_eventos_ids": [],
        "numero_tentativa": 1,
        "feedback_tutor_ia": "",
        "estrategia_financiamento": {},
        "simulacao_finalizada": False,
        "confirmar_encerramento": False,
    }

    for chave, valor in valores_padrao.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor
