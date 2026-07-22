# Registro de Desenvolvimento — STEM FinanceLab v0.5.4

## Finalidade

Preparar a aplicação para implantação web piloto, com foco em estabilidade, configuração e diagnóstico de falhas.

## Alterações realizadas

- centralização do número da versão e dos caminhos do projeto;
- caminho do banco configurável por `STEM_FINANCELAB_DB_PATH`;
- criação automática da pasta do banco;
- SQLite configurado com `foreign_keys`, `busy_timeout` e modo WAL;
- tratamento de falha na inicialização do banco sem exposição de detalhes técnicos;
- logs padronizados e configuráveis por nível;
- inclusão de `.streamlit/config.toml` para execução em servidor;
- inclusão de `runtime.txt` e `.env.example`;
- atualização do rodapé e do relatório para a versão 0.5.4.

## Limitação conhecida do piloto

Em hospedagens com sistema de arquivos efêmero, o SQLite pode ser reiniciado quando a aplicação é reconstruída ou reiniciada. A versão piloto é adequada para validação funcional. A coleta oficial deverá utilizar armazenamento persistente.
