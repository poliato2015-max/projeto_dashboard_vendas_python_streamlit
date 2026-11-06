"""Leitura do banco SQLite utilizado pelo dashboard de vendas.

Este módulo não cria tabelas, não gera dados e não altera o banco.
A preparação da base é realizada separadamente, fora do escopo do projeto
publicado.
"""

from pathlib import Path
import sqlite3
import pandas as pd

DATABASE_PATH = Path(__file__).resolve().parent / "database.db"
TABLE_NAME = "tb_vendas"
METAS_TABLE_NAME = "tb_metas"

def criar_conexao(db_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Abre uma conexão com um banco SQLite existente.

    Args:
        db_path: Caminho do arquivo SQLite.

    Returns:
        Uma conexão aberta com o banco SQLite.

    Raises:
        FileNotFoundError: Se o arquivo do banco não existir.
    """
    db_path = Path(db_path)

    if not db_path.exists():
        raise FileNotFoundError(
            f"Banco de dados não encontrado: {db_path}"
        )

    if not db_path.is_file():
        raise FileNotFoundError(
            f"O caminho informado não é um arquivo: {db_path}"
        )

    return sqlite3.connect(db_path)

def carregar_dados(db_path: Path = DATABASE_PATH) -> pd.DataFrame:
    """Carrega a tabela de vendas em um DataFrame do Pandas.

    A função realiza somente a leitura da tabela ``tb_vendas``. Ela não cria
    o banco, não cria a tabela e não insere ou modifica registros.

    Args:
        db_path: Caminho do arquivo SQLite.

    Returns:
        DataFrame contendo os registros da tabela ``tb_vendas``.

    Raises:
        FileNotFoundError: Se o arquivo do banco não existir.
        sqlite3.Error: Se ocorrer um erro durante a conexão ou consulta.
    """
    conn = criar_conexao(db_path)

    try:
        return pd.read_sql_query(
            f"SELECT * FROM {TABLE_NAME}",
            conn,
            parse_dates=["date"],
        )
    finally:
        conn.close()

def carregar_metas(db_path: Path = DATABASE_PATH) -> pd.DataFrame:
    """Carrega as metas detalhadas da tabela ``tb_metas``.

    A função somente lê as metas já cadastradas no SQLite. O cálculo e a
    geração dos valores são realizados pelo script de preparação da base.
    """
    conn = criar_conexao(db_path)

    try:
        return pd.read_sql_query(
            f"""
            SELECT periodo, regiao, categoria, produto,
                   meta_faturamento, origem
            FROM {METAS_TABLE_NAME}
            ORDER BY periodo, regiao, categoria, produto
            """,
            conn,
        )
    finally:
        conn.close()