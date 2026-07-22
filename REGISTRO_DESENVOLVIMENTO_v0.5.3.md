# Registro de Desenvolvimento — STEM FinanceLab v0.5.3

## Evolução 002 — Gerenciamento do ciclo de vida da simulação

### Problema identificado
O participante não possuía uma forma explícita de encerrar a experiência durante ou após a missão. O fechamento do navegador não produzia um encerramento controlado nem registrava a interrupção da tentativa.

### Solução implementada
- botão discreto **Encerrar sessão** nas etapas ativas;
- confirmação obrigatória para evitar saídas acidentais;
- atualização da simulação para o status `interrompida`;
- tela final com **Jogar novamente** e **Encerrar sessão**;
- tela de agradecimento e retorno à página inicial;
- seção **Sobre esta pesquisa** na abertura.

### Justificativa pedagógica e de usabilidade
O fluxo respeita a autonomia do participante sem estimular abandono acidental. Ao concluir a missão, oferece uma decisão clara entre repetir a experiência e encerrar a participação.

### Contribuição para a pesquisa
O registro de tentativas concluídas e interrompidas permite avaliar permanência, abandono e repetição, apoiando a análise de usabilidade e engajamento do artefato.
