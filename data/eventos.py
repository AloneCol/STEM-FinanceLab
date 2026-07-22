from random import sample

EVENTOS = [

    {
        "id": 1,
        "titulo": "Falha nos equipamentos",
        "descricao": (
            "Durante a montagem do evento, o projetor principal apresentou "
            "defeito e não poderá ser utilizado."
        ),
        "opcoes": [
            {
                "texto": "Alugar equipamento novo",
                "custo": 2500,
                "risco": 10,
                "qualidade": 95,
            },
            {
                "texto": "Usar equipamento reserva",
                "custo": 800,
                "risco": 35,
                "qualidade": 75,
            },
            {
                "texto": "Continuar mesmo assim",
                "custo": 0,
                "risco": 80,
                "qualidade": 45,
            },
        ],
    },

    {
        "id": 2,
        "titulo": "Cancelamento de palestrante",

        "descricao": (
            "O palestrante principal cancelou sua participação um dia antes "
            "do evento."
        ),

        "opcoes": [

            {
                "texto": "Contratar outro palestrante",

                "custo": 4000,

                "risco": 10,

                "qualidade": 95,
            },

            {
                "texto": "Remanejar programação",

                "custo": 1200,

                "risco": 40,

                "qualidade": 75,
            },

            {
                "texto": "Cancelar palestra",

                "custo": 0,

                "risco": 90,

                "qualidade": 40,
            },

        ],

    },

    {
        "id": 3,

        "titulo": "Problemas com coffee-break",

        "descricao": (
            "O fornecedor informou atraso na entrega do coffee-break."
        ),

        "opcoes": [

            {
                "texto": "Contratar outro fornecedor",

                "custo": 1800,

                "risco": 15,

                "qualidade": 90,
            },

            {
                "texto": "Aguardar entrega",

                "custo": 0,

                "risco": 55,

                "qualidade": 65,
            },

            {
                "texto": "Cancelar coffee-break",

                "custo": 0,

                "risco": 90,

                "qualidade": 30,
            },

        ],

    },

]
EVENTOS.append(
    {
        "id": 4,
        "tipo_evento": "cancelamento_inscricoes",
        "titulo": "Cancelamentos e inadimplência de inscrições",
        "descricao": (
            "Após o período de inscrições, parte dos participantes solicitou "
            "cancelamento e alguns valores ainda não foram recebidos. A decisão "
            "afetará o Banco Conta Movimento, o Contas a Receber e a receita do projeto."
        ),
        "opcoes": [
            {
                "texto": "Reembolsar integralmente e preservar a experiência do participante",
                "custo": 0,
                "percentual_reembolso_recebido": 0.08,
                "percentual_baixa_a_receber": 0.20,
                "risco": 15,
                "qualidade": 95,
            },
            {
                "texto": "Aplicar reembolso parcial conforme política do evento",
                "custo": 0,
                "percentual_reembolso_recebido": 0.04,
                "percentual_baixa_a_receber": 0.15,
                "risco": 40,
                "qualidade": 75,
            },
            {
                "texto": "Não realizar reembolso dos valores já pagos",
                "custo": 0,
                "percentual_reembolso_recebido": 0.0,
                "percentual_baixa_a_receber": 0.10,
                "risco": 85,
                "qualidade": 40,
            },
        ],
    }
)

EVENTOS.extend(
    [
        {
            "id": 5,
            "titulo": "Instabilidade na internet",
            "descricao": (
                "A conexão principal apresentou instabilidade pouco antes das atividades "
                "que dependem de transmissão e credenciamento digital."
            ),
            "opcoes": [
                {"texto": "Contratar conexão de contingência", "custo": 1200, "risco": 10, "qualidade": 95},
                {"texto": "Usar roteadores móveis da equipe", "custo": 350, "risco": 45, "qualidade": 70},
                {"texto": "Manter apenas a conexão disponível", "custo": 0, "risco": 85, "qualidade": 40},
            ],
        },
        {
            "id": 6,
            "titulo": "Exigência adicional de segurança",
            "descricao": (
                "A administração do local solicitou reforço de segurança e controle de acesso "
                "para manter o evento conforme as regras do espaço."
            ),
            "opcoes": [
                {"texto": "Contratar equipe completa de apoio", "custo": 1600, "risco": 10, "qualidade": 95},
                {"texto": "Reorganizar a equipe interna e contratar apoio parcial", "custo": 700, "risco": 40, "qualidade": 75},
                {"texto": "Manter a estrutura originalmente prevista", "custo": 0, "risco": 90, "qualidade": 35},
            ],
        },
        {
            "id": 7,
            "titulo": "Mudança de sala no dia do evento",
            "descricao": (
                "A sala principal ficou indisponível e a organização precisa adaptar rapidamente "
                "a estrutura para outro espaço."
            ),
            "opcoes": [
                {"texto": "Contratar apoio para transferência e nova montagem", "custo": 1400, "risco": 15, "qualidade": 90},
                {"texto": "Realizar a adaptação com a própria equipe", "custo": 450, "risco": 50, "qualidade": 70},
                {"texto": "Reduzir parte da estrutura planejada", "custo": 100, "risco": 75, "qualidade": 50},
            ],
        },
    ]
)
