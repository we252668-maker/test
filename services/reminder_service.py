from __future__ import annotations

import sqlite3
from datetime import datetime

from models.reminder import Reminder


REMINDER_SELECT_FIELDS = """
    id,
    title,
    category,
    description,
    due_at,
    priority,
    status,
    discord_creation_notice_sent_at,
    discord_due_notice_sent_at,
    last_discord_error,
    created_at,
    updated_at
"""


class ReminderService:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def list_reminders(self) -> list[Reminder]:
        cursor = self.connection.cursor()
        cursor.execute(
            f"""
            SELECT {REMINDER_SELECT_FIELDS}
            FROM reminders
            ORDER BY
                CASE WHEN due_at = '' THEN 1 ELSE 0 END,
                due_at ASC,
                id DESC
            """
        )
        return [self._map_row(row) for row in cursor.fetchall()]

    def search_reminders(self, keyword: str) -> list[Reminder]:
        cursor = self.connection.cursor()
        normalized = f"%{keyword.strip()}%"
        cursor.execute(
            f"""
            SELECT {REMINDER_SELECT_FIELDS}
            FROM reminders
            WHERE title LIKE ? OR category LIKE ? OR description LIKE ? OR due_at LIKE ?
            ORDER BY
                CASE WHEN due_at = '' THEN 1 ELSE 0 END,
                due_at ASC,
                id DESC
            """,
            (normalized, normalized, normalized, normalized),
        )
        return [self._map_row(row) for row in cursor.fetchall()]

    def get_reminder_by_id(self, reminder_id: int) -> Reminder | None:
        cursor = self.connection.cursor()
        cursor.execute(
            f"""
            SELECT {REMINDER_SELECT_FIELDS}
            FROM reminders
            WHERE id = ?
            """,
            (reminder_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._map_row(row)

    def get_due_discord_reminders(self) -> list[Reminder]:
        cursor = self.connection.cursor()
        cursor.execute(
            f"""
            SELECT {REMINDER_SELECT_FIELDS}
            FROM reminders
            WHERE
                status = 'pending'
                AND due_at != ''
                AND discord_due_notice_sent_at = ''
                AND datetime(due_at) <= datetime('now', 'localtime')
            ORDER BY due_at ASC, id ASC
            """
        )
        return [self._map_row(row) for row in cursor.fetchall()]

    def create_reminder(
        self,
        title: str,
        category: str,
        description: str,
        due_at: str,
        priority: int,
        status: str,
    ) -> Reminder:
        timestamp = self._current_timestamp()
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO reminders (
                title,
                category,
                description,
                due_at,
                priority,
                status,
                discord_creation_notice_sent_at,
                discord_due_notice_sent_at,
                last_discord_error,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, '', '', '', ?, ?)
            """,
            (
                title.strip(),
                category.strip() or "未分類",
                description.strip(),
                due_at.strip(),
                priority,
                status,
                timestamp,
                timestamp,
            ),
        )
        self.connection.commit()
        return self.get_reminder_by_id(cursor.lastrowid)  # type: ignore[return-value]

    def update_reminder(
        self,
        reminder_id: int,
        title: str,
        category: str,
        description: str,
        due_at: str,
        priority: int,
        status: str,
    ) -> Reminder | None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE reminders
            SET
                title = ?,
                category = ?,
                description = ?,
                due_at = ?,
                priority = ?,
                status = ?,
                discord_due_notice_sent_at = '',
                last_discord_error = '',
                updated_at = ?
            WHERE id = ?
            """,
            (
                title.strip(),
                category.strip() or "未分類",
                description.strip(),
                due_at.strip(),
                priority,
                status,
                self._current_timestamp(),
                reminder_id,
            ),
        )
        self.connection.commit()
        if cursor.rowcount == 0:
            return None
        return self.get_reminder_by_id(reminder_id)

    def delete_reminder(self, reminder_id: int) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def mark_discord_creation_notice_sent(self, reminder_id: int | None) -> None:
        if reminder_id is None:
            return
        now = self._current_timestamp()
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE reminders
            SET discord_creation_notice_sent_at = ?, last_discord_error = '', updated_at = ?
            WHERE id = ?
            """,
            (now, now, reminder_id),
        )
        self.connection.commit()

    def mark_discord_due_notice_sent(self, reminder_id: int | None) -> None:
        if reminder_id is None:
            return
        now = self._current_timestamp()
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE reminders
            SET discord_due_notice_sent_at = ?, last_discord_error = '', updated_at = ?
            WHERE id = ?
            """,
            (now, now, reminder_id),
        )
        self.connection.commit()

    def mark_discord_failed(self, reminder_id: int | None, error_message: str) -> None:
        if reminder_id is None:
            return
        safe_error = error_message.strip()[:500]
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE reminders
            SET last_discord_error = ?, updated_at = ?
            WHERE id = ?
            """,
            (safe_error, self._current_timestamp(), reminder_id),
        )
        self.connection.commit()

    def _map_row(self, row: sqlite3.Row) -> Reminder:
        return Reminder(
            id=row["id"],
            title=row["title"],
            category=row["category"],
            description=row["description"],
            due_at=row["due_at"],
            priority=row["priority"],
            status=row["status"],
            discord_creation_notice_sent_at=row["discord_creation_notice_sent_at"],
            discord_due_notice_sent_at=row["discord_due_notice_sent_at"],
            last_discord_error=row["last_discord_error"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _current_timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
