"""Configurações centralizadas do STEM FinanceLab."""
from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "STEM FinanceLab"
APP_VERSION = "0.5.4"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "database" / "stem_financelab.db"


def obter_caminho_banco() -> Path:
    """Permite configurar o banco por variável de ambiente em hospedagens web."""
    configurado = os.getenv("STEM_FINANCELAB_DB_PATH", "").strip()
    caminho = Path(configurado).expanduser() if configurado else DEFAULT_DB_PATH
    if not caminho.is_absolute():
        caminho = PROJECT_ROOT / caminho
    return caminho.resolve()
