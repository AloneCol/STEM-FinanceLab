"""Configurações centralizadas do STEM FinanceLab."""
from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "STEM FinanceLab"
APP_VERSION = "0.5.6"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "database" / "stem_financelab.db"


def obter_caminho_banco() -> Path:
    """Permite configurar o banco por variável de ambiente em hospedagens web."""
    configurado = os.getenv("STEM_FINANCELAB_DB_PATH", "").strip()
    caminho = Path(configurado).expanduser() if configurado else DEFAULT_DB_PATH
    if not caminho.is_absolute():
        caminho = PROJECT_ROOT / caminho
    return caminho.resolve()


# ---------------------------------------------------------------------------
# Modo pesquisa: ativa o fluxo de TCLE completo e o campo de identificação
# por código/apelido, usado durante a coleta oficial de dados da dissertação.
# Fora deste modo (padrão), o sistema mantém o comportamento público atual.
# Ativar definindo a variável de ambiente STEM_FINANCELAB_MODO_PESQUISA=true
# nos "Secrets" do Streamlit Community Cloud durante o período de coleta.
# ---------------------------------------------------------------------------
MODO_PESQUISA = os.getenv("STEM_FINANCELAB_MODO_PESQUISA", "false").strip().lower() == "true"
