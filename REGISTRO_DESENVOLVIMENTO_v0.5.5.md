# Registro de Desenvolvimento — STEM FinanceLab v0.5.5

## Finalidade

Correção de usabilidade da etapa de eventos inesperados em dispositivos móveis.

## Problema identificado

Após confirmar uma decisão, a atualização da página podia manter a posição de rolagem próxima ao botão. Assim, o evento seguinte era exibido fora do início da tela e o participante poderia não perceber a descrição antes de interagir com as alternativas.

## Alterações realizadas

- reposicionamento automático da tela no início ao entrar em cada evento inesperado;
- remoção da alternativa selecionada por padrão;
- exigência de seleção consciente antes da exibição dos impactos e do botão de confirmação;
- inclusão de mensagem orientativa para leitura da descrição do imprevisto;
- atualização da versão para v0.5.5.

## Resultado esperado

O participante passa a visualizar primeiro o título e a descrição do imprevisto e não consegue confirmar uma opção sem selecioná-la explicitamente.
