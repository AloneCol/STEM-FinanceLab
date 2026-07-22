# STEM FinanceLab v0.5.4 — Web Release Candidate

Serious Game de gestão financeira para desenvolvimento de competências de planejamento, análise e tomada de decisão em projetos STEM.

## Execução local

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Tutor Inteligente

A IA é complementar. Sem chave, a simulação continua funcionando com feedback baseado em regras.

Para uso local, copie `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` e informe:

```toml
OPENAI_API_KEY = "sua_chave"
OPENAI_MODEL = "gpt-5-mini"
```

Nunca envie o arquivo real de segredos ao GitHub.

## Implantação no Streamlit Community Cloud

1. Crie um repositório no GitHub e envie o conteúdo desta pasta.
2. No painel do Streamlit Community Cloud, selecione o repositório.
3. Defina `app.py` como arquivo principal.
4. Em **Secrets**, cadastre `OPENAI_API_KEY` e, opcionalmente, `OPENAI_MODEL`.
5. Publique e execute os testes do roteiro `TESTE_WEB_PILOTO.md`.

## Banco de dados

O banco SQLite é criado automaticamente em `database/stem_financelab.db`.
O caminho pode ser alterado pela variável:

```text
STEM_FINANCELAB_DB_PATH=/caminho/persistente/stem_financelab.db
```

**Atenção:** em serviços com armazenamento efêmero, o banco local pode ser perdido após reinicializações ou novos deployments. Use esta versão para piloto funcional; a coleta oficial deve usar armazenamento persistente.

## Arquivos de implantação

- `requirements.txt`: dependências Python;
- `runtime.txt`: versão do Python;
- `.streamlit/config.toml`: configuração do servidor;
- `.streamlit/secrets.toml.example`: modelo de segredos;
- `.env.example`: variáveis opcionais;
- `.gitignore`: exclusão de credenciais, ambientes e banco local.
