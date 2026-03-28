from __future__ import annotations

import sqlite3

from models.attachment import Attachment


class AttachmentService:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_attachments(self, owner_type: str, owner_id: int) -> list[Attachment]:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT id, owner_type, owner_id, file_name, stored_path, mime_type,
                   file_size, checksum, created_by, created_at
            FROM attachments
            WHERE owner_type = ? AND owner_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (owner_type, owner_id),
        )
        return [
            Attachment(
                id=row["id"],
                owner_type=row["owner_type"],
                owner_id=row["owner_id"],
                file_name=row["file_name"],
                stored_path=row["stored_path"],
                mime_type=row["mime_type"],
                file_size=row["file_size"],
                checksum=row["checksum"],
                created_by=row["created_by"],
                created_at=row["created_at"],
            )
            for row in cursor.fetchall()
        ]
