import sqlite3
from datetime import UTC, datetime

SCHEMA = """
CREATE TABLE IF NOT EXISTS research_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    category TEXT,
    status TEXT NOT NULL DEFAULT 'inbox',
    research TEXT,
    research_error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS research_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    research_item_id INTEGER NOT NULL,
    chat_id INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (research_item_id)
        REFERENCES research_items(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS research_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (session_id)
        REFERENCES research_sessions(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_research_sessions_item
ON research_sessions(research_item_id);

CREATE INDEX IF NOT EXISTS idx_research_messages_session
ON research_messages(session_id);
"""


def now() -> str:
    return datetime.now(UTC).isoformat()


class ResearchRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add_research_item(
        self,
        content: str,
        category: str,
    ) -> int:
        now = datetime.now(UTC).isoformat()

        cursor = self.connection.execute(
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

        self.connection.commit()

        return cursor.lastrowid

    def delete_research_item(self, id: str) -> None:
        self.connection.execute(
            """
            Delete from research_items where (id=?)
            """,
            (id,),
        )
        self.connection.commit()

    def clear_research_items(
        self,
    ) -> None:
        self.connection.execute(
            """
            Delete from research_items where 1=1
            """
        )
        self.connection.commit()

    def list_research_items(
        self,
    ) -> list[sqlite3.Row]:
        return  self.connection.execute(
            """
            SELECT id, content, category, status, created_at
            FROM research_items
            ORDER BY created_at DESC
            """
        ).fetchall()

    def get_research_item(self, item_id: int) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT *
            FROM research_items
            WHERE id = ?
            """,
            (item_id,),
        ).fetchone()

    def create_session(self, item_id: int, chat_id: int) -> int:
        timestamp = now()

        cursor = self.connection.execute(
            """
            INSERT INTO research_sessions (
                research_item_id,
                chat_id,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (item_id, chat_id, timestamp, timestamp),
        )

        self.connection.commit()

        return int(cursor.lastrowid)

    def set_session_chat(self, session_id: int, chat_id: int) -> None:
        self.connection.execute(
            """
            UPDATE research_sessions
            SET chat_id = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (chat_id, now(), session_id),
        )

        self.connection.commit()

    def get_active_session_for_chat(
        self,
        chat_id: int,
    ) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT *
            FROM research_sessions
            WHERE chat_id = ?
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (chat_id,),
        ).fetchone()

    def get_session_for_item(
        self,
        item_id: int,
    ) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT *
            FROM research_sessions
            WHERE research_item_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (item_id,),
        ).fetchone()

    def add_message(
        self,
        session_id: int,
        role: str,
        content: str,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO research_messages (
                session_id,
                role,
                content,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (session_id, role, content, now()),
        )

        self.connection.execute(
            """
            UPDATE research_sessions
            SET updated_at = ?
            WHERE id = ?
            """,
            (now(), session_id),
        )

        self.connection.commit()

    def get_messages(
        self,
        session_id: int,
    ) -> list[sqlite3.Row]:
        return list(
            self.connection.execute(
                """
                SELECT role, content
                FROM research_messages
                WHERE session_id = ?
                ORDER BY id
                """,
                (session_id,),
            )
        )

    def update_research(
        self,
        item_id: int,
        research: str,
        status: str = "review",
    ) -> None:
        self.connection.execute(
            """
            UPDATE research_items
            SET research = ?,
                status = ?,
                research_error = NULL,
                updated_at = ?
            WHERE id = ?
            """,
            (research, status, now(), item_id),
        )

        self.connection.commit()

    def set_item_status(self, item_id: int, status: str) -> None:
        self.connection.execute(
            """
            UPDATE research_items
            SET status = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (status, now(), item_id),
        )

        self.connection.commit()

    def set_item_error(self, item_id: int, error: str) -> None:
        self.connection.execute(
            """
            UPDATE research_items
            SET status = 'failed',
                research_error = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (error, now(), item_id),
        )

        self.connection.commit()

    def approve_research_item(self, item_id: int) -> None:
        self.connection.execute(
            """
            UPDATE research_items
            SET status = 'approved',
                updated_at = ?
            WHERE id = ?
            """,
            (now(), item_id),
        )

        self.connection.commit()

    def get_session(
        self,
        session_id: int,
    ) -> sqlite3.Row | None:
        return self.connection.execute(
            """
            SELECT *
            FROM research_sessions
            WHERE id = ?
            """,
            (session_id,),
        ).fetchone()