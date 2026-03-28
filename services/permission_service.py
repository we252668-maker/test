from __future__ import annotations

import sqlite3

from models.session_context import SessionContext


class PermissionService:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def has_permission(self, session: SessionContext, permission_code: str) -> bool:
        if session.is_system_admin:
            return True
        if session.user_id is None:
            return False

        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT 1
            FROM user_roles ur
            INNER JOIN role_permissions rp ON rp.role_id = ur.role_id
            INNER JOIN permissions p ON p.id = rp.permission_id
            WHERE ur.user_id = ? AND p.code = ?
            LIMIT 1
            """,
            (session.user_id, permission_code),
        )
        return cursor.fetchone() is not None
