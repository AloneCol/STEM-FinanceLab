# Registro de desenvolvimento — versão 0.5.0

## Objetivo da evolução

A versão 0.5.0 consolida a identidade do STEM FinanceLab como um jogo estratégico de gerenciamento de recursos para o ensino de princípios financeiros a profissionais e estudantes das áreas STEM. A evolução foi concentrada na experiência inicial, na contextualização da missão e no registro estruturado das tentativas, sem alterar o motor financeiro determinístico já validado nas versões anteriores.

## Alterações implementadas

1. Inclusão do nome ou identificação do participante, instituição e curso no cadastro inicial.
2. Seleção da missão antes do diagnóstico, com três cenários: Workshop de Tecnologia, Seminário de Inovação e Congresso STEM.
3. Apresentação de briefing com orçamento, capacidade e objetivo geral da missão.
4. Adequação da linguagem da interface para os termos gestor, missão, planejamento estratégico e desafios estratégicos.
5. Inclusão da tabela `simulacoes`, que registra participante, missão, número da tentativa, início, término, status, lucro, saldo de caixa e resumo dos resultados.
6. Migração automática do banco de dados para preservar compatibilidade com registros das versões anteriores.
7. Atualização do relatório HTML para apresentar o nome do gestor, instituição, curso e a versão 0.5.0.

## Decisão arquitetural

O motor financeiro não foi modificado. A separação entre a camada de experiência do jogo e o núcleo de cálculo reduz o risco de regressões e preserva a rastreabilidade dos resultados. Os valores financeiros continuam sendo calculados por regras determinísticas; a inteligência artificial permanece restrita à interpretação pedagógica dos resultados.

## Contribuição para a pesquisa

O registro de cada tentativa permite acompanhar o uso do artefato e produzir análises sobre missão escolhida, repetição, conclusão, lucro e disponibilidade financeira. Esses dados podem complementar questionários de usabilidade e percepção de aprendizagem durante a avaliação do artefato.
