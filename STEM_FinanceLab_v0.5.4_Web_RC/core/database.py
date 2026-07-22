import json
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Optional

from core.config import obter_caminho_banco


def conectar() -> sqlite3.Connection:
    """Abre uma conexão SQLite preparada para uso concorrente moderado."""
    db_path = obter_caminho_banco()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(db_path, timeout=30.0)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.execute("PRAGMA busy_timeout = 30000")
    return conexao


def inicializar_banco() -> None:
    with conectar() as conexao:
        # WAL reduz bloqueios de leitura/escrita em acessos simultâneos.
        conexao.execute("PRAGMA journal_mode = WAL")
        conexao.execute("PRAGMA synchronous = NORMAL")
        conexao.executescript(
            """
            CREATE TABLE IF NOT EXISTS participantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT NOT NULL UNIQUE,
                nome TEXT,
                instituicao TEXT,
                curso TEXT,
                area TEXT NOT NULL,
                perfil TEXT NOT NULL,
                experiencia TEXT NOT NULL,
                experiencia_gestao TEXT NOT NULL,
                criado_em TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS diagnosticos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participante_id INTEGER NOT NULL,
                respostas_json TEXT NOT NULL,
                observacao TEXT,
                criado_em TEXT NOT NULL,
                FOREIGN KEY (participante_id)
                    REFERENCES participantes(id)
            );

            CREATE TABLE IF NOT EXISTS planejamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participante_id INTEGER NOT NULL,
                alocacoes_json TEXT NOT NULL,
                escolhas_json TEXT NOT NULL,
                resumo_json TEXT NOT NULL,
                criado_em TEXT NOT NULL,
                FOREIGN KEY (participante_id)
                    REFERENCES participantes(id)
            );

            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participante_id INTEGER NOT NULL,
                evento_id INTEGER NOT NULL,
                titulo TEXT NOT NULL,
                opcao TEXT NOT NULL,
                custo REAL NOT NULL,
                risco INTEGER NOT NULL,
                qualidade INTEGER NOT NULL,
                data_registro TEXT NOT NULL,
                FOREIGN KEY (participante_id)
                    REFERENCES participantes(id)
            );

            CREATE TABLE IF NOT EXISTS estrategias_financiamento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participante_id INTEGER NOT NULL,
                simulacao_id INTEGER,
                modelo TEXT NOT NULL,
                publico_previsto INTEGER NOT NULL,
                pagantes_previstos INTEGER NOT NULL,
                valor_inscricao REAL NOT NULL,
                recurso_inicial REAL NOT NULL,
                proposta TEXT,
                apoio_externo REAL NOT NULL,
                recursos_totais REAL NOT NULL,
                detalhes_json TEXT,
                criado_em TEXT NOT NULL,
                FOREIGN KEY (participante_id) REFERENCES participantes(id),
                FOREIGN KEY (simulacao_id) REFERENCES simulacoes(id)
            );

            CREATE TABLE IF NOT EXISTS simulacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participante_id INTEGER NOT NULL,
                missao TEXT NOT NULL,
                tentativa INTEGER NOT NULL DEFAULT 1,
                iniciado_em TEXT NOT NULL,
                finalizado_em TEXT,
                status TEXT NOT NULL DEFAULT 'em_andamento',
                lucro REAL,
                saldo_caixa REAL,
                resultado_json TEXT,
                FOREIGN KEY (participante_id)
                    REFERENCES participantes(id)
            );
            """
        )

        # Migração compatível com bancos criados em versões anteriores.
        colunas = {linha["name"] for linha in conexao.execute("PRAGMA table_info(participantes)")}
        for coluna in ("nome", "instituicao", "curso"):
            if coluna not in colunas:
                conexao.execute(f"ALTER TABLE participantes ADD COLUMN {coluna} TEXT")


def salvar_participante(
    nome: str,
    instituicao: str,
    curso: str,
    area: str,
    perfil: str,
    experiencia: str,
    experiencia_gestao: str,
) -> int:
    criado_em = datetime.now(timezone.utc).isoformat()

    with conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO participantes
                (codigo, nome, instituicao, curso, area, perfil, experiencia, experiencia_gestao, criado_em)
            VALUES
                ('TEMP', ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (nome.strip(), instituicao.strip(), curso.strip(), area, perfil, experiencia, experiencia_gestao, criado_em),
        )
        participante_id = int(cursor.lastrowid)
        codigo = f"STEM-{participante_id:04d}"
        conexao.execute(
            "UPDATE participantes SET codigo = ? WHERE id = ?",
            (codigo, participante_id),
        )
        return participante_id


def salvar_diagnostico(
    participante_id: int,
    respostas: Dict[str, int],
    observacao: str,
) -> None:
    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO diagnosticos
                (participante_id, respostas_json, observacao, criado_em)
            VALUES
                (?, ?, ?, ?)
            """,
            (
                participante_id,
                json.dumps(respostas, ensure_ascii=False),
                observacao.strip(),
                datetime.now(timezone.utc).isoformat(),
            ),
        )


def salvar_planejamento(participante_id: int, alocacoes: Dict[str,float], escolhas: Dict[str,Dict[str,float]], resumo: Dict[str,float]) -> None:
    with conectar() as conexao:
        conexao.execute(
            """INSERT INTO planejamentos (participante_id, alocacoes_json, escolhas_json, resumo_json, criado_em) VALUES (?, ?, ?, ?, ?)""",
            (participante_id, json.dumps(alocacoes, ensure_ascii=False), json.dumps(escolhas, ensure_ascii=False), json.dumps(resumo, ensure_ascii=False), datetime.now(timezone.utc).isoformat())
        )

def salvar_evento(
    participante_id: int,
    evento_id: int,
    titulo: str,
    opcao: str,
    custo: float,
    risco: int,
    qualidade: int,
) -> None:
    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO eventos (
                participante_id,
                evento_id,
                titulo,
                opcao,
                custo,
                risco,
                qualidade,
                data_registro
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                participante_id,
                evento_id,
                titulo,
                opcao,
                custo,
                risco,
                qualidade,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        
def listar_eventos(participante_id: int):
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            SELECT
                evento_id,
                titulo,
                opcao,
                custo,
                risco,
                qualidade,
                data_registro
            FROM eventos
            WHERE participante_id = ?
            ORDER BY id
            """,
            (participante_id,),
        )

        return cursor.fetchall()

def iniciar_simulacao(participante_id: int, missao: str, tentativa: int) -> int:
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO simulacoes
                (participante_id, missao, tentativa, iniciado_em, status)
            VALUES (?, ?, ?, ?, 'em_andamento')
            """,
            (participante_id, missao, tentativa, datetime.now(timezone.utc).isoformat()),
        )
        return int(cursor.lastrowid)


def finalizar_simulacao(
    simulacao_id: int,
    lucro: float,
    saldo_caixa: float,
    resultado: Optional[Dict] = None,
) -> None:
    with conectar() as conexao:
        conexao.execute(
            """
            UPDATE simulacoes
            SET finalizado_em = ?, status = 'concluida', lucro = ?, saldo_caixa = ?, resultado_json = ?
            WHERE id = ? AND status <> 'concluida'
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                float(lucro),
                float(saldo_caixa),
                json.dumps(resultado or {}, ensure_ascii=False),
                simulacao_id,
            ),
        )


def interromper_simulacao(simulacao_id: int) -> None:
    """Marca uma tentativa em andamento como interrompida."""
    with conectar() as conexao:
        conexao.execute(
            """
            UPDATE simulacoes
            SET finalizado_em = ?, status = 'interrompida'
            WHERE id = ? AND status = 'em_andamento'
            """,
            (datetime.now(timezone.utc).isoformat(), simulacao_id),
        )


def salvar_estrategia_financiamento(
    participante_id: int,
    simulacao_id: int | None,
    estrategia: Dict,
) -> None:
    with conectar() as conexao:
        conexao.execute(
            """
            INSERT INTO estrategias_financiamento (
                participante_id, simulacao_id, modelo, publico_previsto,
                pagantes_previstos, valor_inscricao, recurso_inicial, proposta,
                apoio_externo, recursos_totais, detalhes_json, criado_em
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                participante_id, simulacao_id, estrategia.get("modelo", ""),
                int(estrategia.get("publico_previsto", 0)),
                int(estrategia.get("pagantes_previstos", 0)),
                float(estrategia.get("valor_inscricao", 0)),
                float(estrategia.get("recurso_inicial", 0)),
                estrategia.get("proposta", ""),
                float(estrategia.get("apoio_externo", 0)),
                float(estrategia.get("recursos_disponiveis", 0)),
                json.dumps(estrategia, ensure_ascii=False),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
