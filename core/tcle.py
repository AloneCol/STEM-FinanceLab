"""Termo de Consentimento Livre e Esclarecido (TCLE) exibido no modo pesquisa.

Este módulo só é usado quando core.config.MODO_PESQUISA está ativo. Fora da
coleta oficial de dados, a tela inicial mantém o texto de consentimento
resumido já existente em app.py.

ATENÇÃO: os trechos marcados com [A PREENCHER] dependem do parecer do Comitê
de Ética em Pesquisa (CEP) e da Carta de Anuência da instituição, e não devem
ser inventados. Preencha-os assim que o CEP aprovar o projeto, antes de
ativar o modo pesquisa em produção.
"""
from __future__ import annotations

TCLE_TEXTO = """
### Termo de Consentimento Livre e Esclarecido (TCLE)

**Título da pesquisa:** Um Simulador Educacional Gamificado de Gestão Financeira
de Eventos Acadêmicos para Estudantes e Profissionais de STEM

**Pesquisador responsável:** Ricardo Souza de Oliveira
**Orientador:** Prof. Dr. Jefferson Oliveira Andrade
**Coorientadora:** Prof.ª Dr.ª Luciana Lee
**Instituição:** Instituto Federal do Espírito Santo (Ifes), Programa de
Pós-Graduação em Computação Aplicada (PPCOMP)

**1. Convite e objetivo.** Você está sendo convidado a participar de uma
pesquisa de mestrado que avalia este simulador quanto à aprendizagem de
conceitos básicos de planejamento e controle financeiro e quanto à
usabilidade da ferramenta.

**2. Procedimentos.** A participação envolve responder a um questionário
inicial, utilizar o simulador em uma ou mais sessões completas (20 a 25
minutos) e responder a um questionário final, com perguntas de conhecimento,
percepção e usabilidade.

**3. Riscos e benefícios.** Os riscos são mínimos, limitados a eventual
cansaço ao responder aos questionários. Os benefícios incluem o contato com
uma ferramenta educacional gratuita sobre gestão financeira e a contribuição
para a pesquisa.

**4. Confidencialidade.** Você não deve se identificar pelo nome real neste
simulador. Utilize um código ou apelido de sua escolha, repetido no
questionário inicial e no final, para permitir a comparação de suas
respostas sem identificá-lo. Os resultados são analisados de forma agregada.

**5. Participação voluntária.** A participação é voluntária, e você pode
desistir a qualquer momento, sem necessidade de justificativa e sem
qualquer prejuízo.

**6. Armazenamento.** Os registros do simulador ficam associados apenas ao
código escolhido por você, nunca ao seu nome. [A PREENCHER: prazo de guarda
e procedimento de descarte dos dados, conforme definido com o CEP.]

**7. Contato.** Em caso de dúvidas, entre em contato com o pesquisador
responsável [A PREENCHER: e-mail/telefone] ou com o Comitê de Ética em
Pesquisa do Ifes (CEP/Ifes): Av. Rio Branco, nº 50, Santa Lúcia, Vitória,
ES, CEP 29056-255. Telefones: (27) 92001-6011 e (27) 3357-7518. E-mails:
etica.pesquisa@ifes.edu.br e secretaria.cep@ifes.edu.br. Atendimento de
segunda a sexta-feira, das 8h às 12h. [A PREENCHER após a aprovação:
número do parecer consubstanciado e, se aplicável, do CAAE.]
"""


def tcle_pendente() -> bool:
    """Indica se o texto do TCLE ainda contém lacunas não preenchidas.

    Usado para impedir, por segurança, que o modo pesquisa entre em produção
    com informações de contato do CEP ainda ausentes.
    """
    return "[A PREENCHER" in TCLE_TEXTO
