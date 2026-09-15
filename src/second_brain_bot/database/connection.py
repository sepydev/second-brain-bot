import sqlite3
from pathlib import Path

from second_brain_bot.database.repository import SCHEMA


def create_connection(database_path: Path)-> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
    _migrate(connection)
    connection.commit()


def _migrate(connection: sqlite3.Connection) -> None:
    columns = {
        row["name"]
        for row in connection.execute(
            "PRAGMA table_info(research_sessions)"
        ).fetchall()
    }

    if "chat_id" not in columns:
        connection.execute(
            "ALTER TABLE research_sessions ADD COLUMN chat_id INTEGER"
        )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_research_sessions_chat
        ON research_sessions(chat_id)
        """
    )
