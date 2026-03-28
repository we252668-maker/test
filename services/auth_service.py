from __future__ import annotations

import sqlite3

from models.session_context import SessionContext


class AuthService:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def get_bootstrap_session(self) -> SessionContext:
        # Local desktop fallback for single-user mode.
        return SessionContext()

    def authenticate(self, username: str, password: str) -> SessionContext | None:
        # Placeholder for future login flow. Kept explicit so controllers do not
        # depend on implementation details when auth is introduced.
        _ = password
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT id, username, display_name, is_system_admin
            FROM users
            WHERE username = ? AND status = 'active'
            """,
            (username,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return SessionContext(
            user_id=row["id"],
            username=row["username"],
            display_name=row["display_name"] or row["username"],
            is_authenticated=True,
            is_system_admin=bool(row["is_system_admin"]),
        )
