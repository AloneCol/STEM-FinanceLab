"""Configuração de logs sem registrar dados pessoais ou segredos."""
from __future__ import annotations

import logging
import os


def configurar_logs() -> None:
    nivel_texto = os.getenv("STEM_FINANCELAB_LOG_LEVEL", "INFO").upper()
    nivel = getattr(logging, nivel_texto, logging.INFO)
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
