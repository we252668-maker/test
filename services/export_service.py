from __future__ import annotations

import sqlite3
from datetime import datetime


class ExportService:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def queue_export_job(
        self,
        export_type: str,
        source_type: str,
        source_id: int | None,
        file_path: str,
        requested_by: int | None = None,
    ) -> int:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO export_jobs (
                export_type, source_type, source_id, file_path,
                status, requested_by, requested_at
            )
            VALUES (?, ?, ?, ?, 'pending', ?, ?)
            """,
            (
                export_type,
                source_type,
                source_id,
                file_path,
                requested_by,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        self.connection.commit()
        return int(cursor.lastrowid)
