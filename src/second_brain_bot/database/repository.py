import sqlite3
from datetime import UTC, datetime


def initialize_database(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS research_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'inbox',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    connection.commit()


def add_item(
    connection: sqlite3.Connection,
    content: str,
    category: str,
) -> int:
    now = datetime.now(UTC).isoformat()

    cursor = connection.execute(
        """
        INSERT INTO research_items (
            content,
            category,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, 'inbox', ?, ?)
        """,
        (content, category, now, now),
    )

    connection.commit()

    return cursor.lastrowid

def delete_item(
        connection:sqlite3.Connection,
        id:str
) -> None:
    connection.execute(
     """
     Delete from research_items where (id=?)
     """,
        (id,)
    )
    connection.commit()



def list_items(
    connection: sqlite3.Connection,
) -> list[sqlite3.Row]:
    cursor = connection.execute(
        """
        SELECT id, content, category, status, created_at
        FROM research_items
        ORDER BY created_at DESC
        """
    )

    return cursor.fetchall()