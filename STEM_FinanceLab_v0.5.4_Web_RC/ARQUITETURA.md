# Arquitetura inicial

```text
Usuário
  ↓
Interface Streamlit
  ↓
Controle de sessão
  ↓
Questionário e motor da simulação
  ↓
Motor financeiro
  ↓
SQLite
  ↓
API de IA para feedback pedagógico
```

## Módulos atuais

- `app.py`: navegação e apresentação;
- `core/database.py`: persistência dos dados;
- `core/session.py`: estado da simulação;
- `core/ui.py`: identidade visual;
- `data/questionario.py`: instrumento diagnóstico.

## Módulos planejados

- `core/financeiro.py`;
- `core/simulacao.py`;
- `core/pontuacao.py`;
- `core/ia.py`;
- `data/cenario.py`;
- tabelas de simulações, decisões, eventos e avaliações.

## Camada de Inteligência Artificial — v0.5.0

O módulo `core/tutor_ia.py` atua somente após o encerramento da simulação. Ele
recebe um resumo dos valores calculados pelo motor financeiro e a interpretação
do sistema baseado em regras. A chamada à API não executa cálculos contábeis,
não modifica o estado financeiro e não substitui os demonstrativos. Sua saída é
um feedback pedagógico complementar, organizado em leitura do resultado,
decisão de maior impacto, estratégia para nova tentativa e pergunta reflexiva.
