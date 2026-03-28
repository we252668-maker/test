from __future__ import annotations

import sqlite3
from datetime import datetime

from models.note import Note


class NoteService:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.connection.execute("PRAGMA foreign_keys = ON")

    def list_notes(self) -> list[Note]:
        query = self._build_note_query()
        cursor = self.connection.cursor()
        cursor.execute(query)
        return [self._map_row_to_note(row) for row in cursor.fetchall()]

    def search_notes(self, keyword: str) -> list[Note]:
        normalized = f"%{keyword.strip()}%"
        query = self._build_note_query(
            """
            WHERE
                n.title LIKE :keyword
                OR n.content LIKE :keyword
                OR EXISTS (
                    SELECT 1
                    FROM note_tags search_nt
                    INNER JOIN tags search_t ON search_t.id = search_nt.tag_id
                    WHERE search_nt.note_id = n.id
                    AND search_t.name LIKE :keyword
                )
            """
        )
        cursor = self.connection.cursor()
        cursor.execute(query, {"keyword": normalized})
        return [self._map_row_to_note(row) for row in cursor.fetchall()]

    def get_note_by_id(self, note_id: int) -> Note | None:
        query = self._build_note_query("WHERE n.id = :note_id")
        cursor = self.connection.cursor()
        cursor.execute(query, {"note_id": note_id})
        row = cursor.fetchone()
        if row is None:
            return None
        return self._map_row_to_note(row)

    def create_note(self, title: str, content: str, tags: list[str]) -> Note:
        title = title.strip()
        content = content.strip()
        clean_tags = self._normalize_tags(tags)
        summary = self._build_summary(content)
        timestamp = self._current_timestamp()

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO notes (title, content, summary, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, content, summary, timestamp, timestamp),
        )
        note_id = cursor.lastrowid
        self._replace_note_tags(note_id, clean_tags)
        self.connection.commit()
        return self.get_note_by_id(note_id)  # type: ignore[return-value]

    def update_note(self, note_id: int, title: str, content: str, tags: list[str]) -> Note | None:
        title = title.strip()
        content = content.strip()
        clean_tags = self._normalize_tags(tags)
        summary = self._build_summary(content)
        timestamp = self._current_timestamp()

        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE notes
            SET title = ?, content = ?, summary = ?, updated_at = ?
            WHERE id = ?
            """,
            (title, content, summary, timestamp, note_id),
        )

        if cursor.rowcount == 0:
            self.connection.rollback()
            return None

        self._replace_note_tags(note_id, clean_tags)
        self.connection.commit()
        return self.get_note_by_id(note_id)

    def delete_note(self, note_id: int) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def _replace_note_tags(self, note_id: int, tags: list[str]) -> None:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))

        for tag_name in tags:
            cursor.execute(
                """
                INSERT INTO tags (name)
                VALUES (?)
                ON CONFLICT(name) DO NOTHING
                """,
                (tag_name,),
            )
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            tag_row = cursor.fetchone()
            if tag_row is None:
                continue
            cursor.execute(
                """
                INSERT OR IGNORE INTO note_tags (note_id, tag_id)
                VALUES (?, ?)
                """,
                (note_id, tag_row["id"]),
            )

    def _build_note_query(self, where_clause: str = "") -> str:
        return f"""
            SELECT
                n.id,
                n.title,
                n.content,
                n.summary,
                n.created_at,
                n.updated_at,
                COALESCE(GROUP_CONCAT(t.name, ','), '') AS tags
            FROM notes n
            LEFT JOIN note_tags nt ON nt.note_id = n.id
            LEFT JOIN tags t ON t.id = nt.tag_id
            {where_clause}
            GROUP BY n.id
            ORDER BY
                CASE WHEN n.updated_at = '' THEN n.id END DESC,
                n.updated_at DESC,
                n.id DESC
        """

    def _map_row_to_note(self, row: sqlite3.Row) -> Note:
        tags = [tag.strip() for tag in row["tags"].split(",") if tag.strip()]
        return Note(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            summary=row["summary"],
            tags=tags,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _normalize_tags(self, tags: list[str]) -> list[str]:
        unique_tags: list[str] = []
        seen_tags: set[str] = set()

        for raw_tag in tags:
            tag = raw_tag.strip()
            if not tag:
                continue
            normalized_key = tag.casefold()
            if normalized_key in seen_tags:
                continue
            seen_tags.add(normalized_key)
            unique_tags.append(tag)

        return unique_tags

    def _build_summary(self, content: str, limit: int = 120) -> str:
        compact = " ".join(content.split())
        if len(compact) <= limit:
            return compact
        return f"{compact[:limit].rstrip()}..."

    def _current_timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
