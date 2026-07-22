CENARIOS = {
    "Pequeno": {
        "nome": "Workshop de Tecnologia",
        "porte": "Pequeno",
        "orcamento_inicial": 10_000.0,
        "capacidade": 80,
        "valor_inscricao": 120.0,
        "patrocinio_base": 3_000.0,
    },
    "Médio": {
        "nome": "Seminário de Inovação",
        "porte": "Médio",
        "orcamento_inicial": 25_000.0,
        "capacidade": 180,
        "valor_inscricao": 180.0,
        "patrocinio_base": 8_000.0,
    },
    "Grande": {
        "nome": "Congresso STEM",
        "porte": "Grande",
        "orcamento_inicial": 50_000.0,
        "capacidade": 350,
        "valor_inscricao": 250.0,
        "patrocinio_base": 15_000.0,
    },
}

CATEGORIAS = [
    "Infraestrutura",
    "Equipamentos",
    "Palestrante",
    "Divulgação",
    "Alimentação",
    "Reserva de contingência",
]

OPCOES_TATICAS_BASE = {
    "Infraestrutura": {
        "Auditório universitário": {
            "custos": {"Pequeno": 1_200.0, "Médio": 3_500.0, "Grande": 6_000.0},
            "qualidade": 65,
            "risco": 20,
            "descricao": "Menor custo, estrutura adequada e capacidade limitada.",
        },
        "Centro de convenções": {
            "custos": {"Pequeno": 2_000.0, "Médio": 6_000.0, "Grande": 10_000.0},
            "qualidade": 90,
            "risco": 10,
            "descricao": "Maior conforto e capacidade, com custo mais elevado.",
        },
    },
    "Equipamentos": {
        "Estrutura básica": {
            "custos": {"Pequeno": 800.0, "Médio": 2_500.0, "Grande": 5_000.0},
            "qualidade": 65,
            "risco": 30,
            "descricao": "Recursos essenciais para projeção, áudio e conectividade.",
        },
        "Estrutura avançada": {
            "custos": {"Pequeno": 1_600.0, "Médio": 5_000.0, "Grande": 9_000.0},
            "qualidade": 90,
            "risco": 10,
            "descricao": "Equipamentos redundantes, gravação e suporte técnico.",
        },
    },
    "Palestrante": {
        "Especialista nacional": {
            "custos": {"Pequeno": 2_000.0, "Médio": 3_000.0, "Grande": 4_000.0},
            "qualidade": 75,
            "risco": 15,
            "descricao": "Boa aderência ao tema e custo moderado.",
        },
        "Especialista internacional": {
            "custos": {"Pequeno": 5_000.0, "Médio": 8_000.0, "Grande": 11_000.0},
            "qualidade": 100,
            "risco": 35,
            "descricao": "Maior prestígio, porém com custos e riscos adicionais.",
        },
    },
    "Divulgação": {
        "Divulgação digital": {
            "custos": {"Pequeno": 500.0, "Médio": 1_500.0, "Grande": 2_000.0},
            "qualidade": 65,
            "risco": 25,
            "descricao": "Campanha em redes sociais e canais institucionais.",
        },
        "Campanha ampliada": {
            "custos": {"Pequeno": 1_200.0, "Médio": 3_000.0, "Grande": 5_000.0},
            "qualidade": 90,
            "risco": 15,
            "descricao": "Campanha digital, imprensa, material gráfico e impulsionamento.",
        },
    },
    "Alimentação": {
        "Coffee break básico": {
            "custos": {"Pequeno": 1_000.0, "Médio": 2_500.0, "Grande": 4_000.0},
            "qualidade": 60,
            "risco": 15,
            "descricao": "Atendimento essencial para os participantes.",
        },
        "Coffee break completo": {
            "custos": {"Pequeno": 1_800.0, "Médio": 4_500.0, "Grande": 7_000.0},
            "qualidade": 90,
            "risco": 10,
            "descricao": "Maior variedade e melhor percepção de qualidade.",
        },
    },
}


def obter_cenario(porte: str) -> dict:
    if porte not in CENARIOS:
        raise ValueError(f"Porte de evento inválido: {porte}")
    return CENARIOS[porte].copy()


def obter_opcoes_taticas(porte: str) -> dict:
    if porte not in CENARIOS:
        raise ValueError(f"Porte de evento inválido: {porte}")

    opcoes = {}
    for categoria, alternativas in OPCOES_TATICAS_BASE.items():
        opcoes[categoria] = {}
        for nome, dados in alternativas.items():
            opcoes[categoria][nome] = {
                "custo": dados["custos"][porte],
                "qualidade": dados["qualidade"],
                "risco": dados["risco"],
                "descricao": dados["descricao"],
            }
    return opcoes


OPCOES_TATICAS = obter_opcoes_taticas("Grande")


MODELOS_FINANCIAMENTO = {
    "Evento pago": {
        "descricao": "A receita depende principalmente das inscrições. O preço pode reduzir ou ampliar a adesão.",
        "permite_inscricao": True,
        "gratuito": False,
    },
    "Evento gratuito patrocinado": {
        "descricao": "O público não paga inscrição. A sustentabilidade depende da proposta de patrocínio escolhida.",
        "permite_inscricao": False,
        "gratuito": True,
    },
    "Evento institucional": {
        "descricao": "A instituição financia parte relevante da missão, com menor autonomia sobre o orçamento.",
        "permite_inscricao": False,
        "gratuito": True,
    },
    "Modelo híbrido": {
        "descricao": "Combina inscrições com apoio externo, reduzindo a dependência de uma única fonte.",
        "permite_inscricao": True,
        "gratuito": False,
    },
}

PROPOSTAS_FINANCIAMENTO = {
    "Pequeno": {
        "Patrocínio ágil": {"valor": 3500.0, "risco": 15, "contrapartida": "Exposição da marca nos materiais do evento."},
        "Patrocínio ampliado": {"valor": 6000.0, "risco": 35, "contrapartida": "Estande e destaque na abertura."},
        "Apoio institucional": {"valor": 5000.0, "risco": 10, "contrapartida": "Uso prioritário da estrutura institucional."},
    },
    "Médio": {
        "Patrocínio ágil": {"valor": 9000.0, "risco": 15, "contrapartida": "Exposição da marca nos materiais do evento."},
        "Patrocínio ampliado": {"valor": 15000.0, "risco": 35, "contrapartida": "Estande, fala institucional e destaque na abertura."},
        "Apoio institucional": {"valor": 12000.0, "risco": 10, "contrapartida": "Uso prioritário da estrutura institucional."},
    },
    "Grande": {
        "Patrocínio ágil": {"valor": 18000.0, "risco": 15, "contrapartida": "Exposição da marca nos materiais do evento."},
        "Patrocínio ampliado": {"valor": 30000.0, "risco": 35, "contrapartida": "Estande, fala institucional e destaque na abertura."},
        "Apoio institucional": {"valor": 25000.0, "risco": 10, "contrapartida": "Uso prioritário da estrutura institucional."},
    },
}

def obter_modelos_financiamento() -> dict:
    return {chave: valor.copy() for chave, valor in MODELOS_FINANCIAMENTO.items()}

def obter_propostas_financiamento(porte: str) -> dict:
    if porte not in PROPOSTAS_FINANCIAMENTO:
        raise ValueError(f"Porte de evento inválido: {porte}")
    return {chave: valor.copy() for chave, valor in PROPOSTAS_FINANCIAMENTO[porte].items()}
