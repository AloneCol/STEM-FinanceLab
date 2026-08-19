# STEM FinanceLab v0.5.6

O STEM FinanceLab é um simulador educacional de gestão financeira desenvolvido para auxiliar profissionais STEM na compreensão e aplicação de conceitos relacionados ao planejamento, orçamento, fluxo de caixa, análise financeira e tomada de decisão.

## Execução local

Para executar o sistema localmente, é necessário possuir Python 3.10 ou superior.

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Tutor com Inteligência Artificial

O STEM FinanceLab possui um módulo opcional de Inteligência Artificial para auxiliar na orientação do usuário durante a simulação.

A IA não é responsável pelos cálculos financeiros nem pelas regras principais do simulador. Caso a chave de acesso à API não esteja configurada, o sistema continua funcionando utilizando os feedbacks previamente definidos.

Para utilizar o recurso de IA localmente, copie o arquivo `.streamlit/secrets.toml.example` para `.streamlit/secrets.toml` e configure:

```text
OPENAI_API_KEY = "sua_chave"
OPENAI_MODEL = "gpt-5-mini"
```

A chave de acesso utilizada no ambiente de desenvolvimento não deve ser publicada no GitHub.

## Execução no Streamlit Community Cloud

Para disponibilizar o sistema na Web:

1. Envie os arquivos do projeto para um repositório no GitHub.
2. Acesse o Streamlit Community Cloud e selecione o repositório.
3. Defina `app.py` como arquivo principal da aplicação.
4. Configure `OPENAI_API_KEY` na área de Secrets, caso o módulo de IA seja utilizado.
5. Publique a aplicação e realize os testes previstos em `TESTE_WEB_PILOTO.md`.

## Banco de dados

O STEM FinanceLab utiliza SQLite para armazenamento dos dados da simulação.

O banco é criado automaticamente no seguinte diretório:

```text
database/stem_financelab.db
```

Nesta versão, o banco de dados é utilizado para execução e testes do simulador. Para uma futura aplicação com coleta permanente de dados, será necessário utilizar uma solução de armazenamento adequada ao ambiente de hospedagem.

## Principais arquivos

* `app.py`: arquivo principal da aplicação;
* `requirements.txt`: dependências necessárias para execução;
* `runtime.txt`: definição da versão do Python;
* `.streamlit/config.toml`: configurações utilizadas pelo Streamlit;
* `.streamlit/secrets.toml.example`: exemplo para configuração das credenciais;
* `.env.example`: exemplo de configuração das variáveis de ambiente;
* `.gitignore`: arquivos e diretórios que não devem ser enviados ao repositório.
