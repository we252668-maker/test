from __future__ import annotations

import sqlite3
from datetime import datetime

from models.code_snippet import CodeSnippet


class SnippetService:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.connection.execute("PRAGMA foreign_keys = ON")

    def list_snippets(self) -> list[CodeSnippet]:
        query = self._build_snippet_query()
        cursor = self.connection.cursor()
        cursor.execute(query)
        return [self._map_row(row) for row in cursor.fetchall()]

    def search_snippets(self, keyword: str) -> list[CodeSnippet]:
        normalized = f"%{keyword.strip()}%"
        query = self._build_snippet_query(
            """
            WHERE
                s.title LIKE :keyword
                OR s.language LIKE :keyword
                OR s.code LIKE :keyword
                OR s.description LIKE :keyword
                OR EXISTS (
                    SELECT 1
                    FROM snippet_tags search_st
                    INNER JOIN tags search_t ON search_t.id = search_st.tag_id
                    WHERE search_st.snippet_id = s.id
                    AND search_t.name LIKE :keyword
                )
            """
        )
        cursor = self.connection.cursor()
        cursor.execute(query, {"keyword": normalized})
        return [self._map_row(row) for row in cursor.fetchall()]

    def get_snippet_by_id(self, snippet_id: int) -> CodeSnippet | None:
        query = self._build_snippet_query("WHERE s.id = :snippet_id")
        cursor = self.connection.cursor()
        cursor.execute(query, {"snippet_id": snippet_id})
        row = cursor.fetchone()
        if row is None:
            return None
        return self._map_row(row)

    def create_snippet(
        self,
        title: str,
        language: str,
        code: str,
        description: str,
        tags: list[str],
    ) -> CodeSnippet:
        timestamp = self._current_timestamp()
        clean_tags = self._normalize_tags(tags)
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO code_snippets (title, language, code, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                title.strip(),
                language.strip(),
                code.rstrip(),
                description.strip(),
                timestamp,
                timestamp,
            ),
        )
        snippet_id = cursor.lastrowid
        self._replace_snippet_tags(snippet_id, clean_tags)
        self.connection.commit()
        return self.get_snippet_by_id(snippet_id)  # type: ignore[return-value]

    def update_snippet(
        self,
        snippet_id: int,
        title: str,
        language: str,
        code: str,
        description: str,
        tags: list[str],
    ) -> CodeSnippet | None:
        clean_tags = self._normalize_tags(tags)
        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE code_snippets
            SET title = ?, language = ?, code = ?, description = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                title.strip(),
                language.strip(),
                code.rstrip(),
                description.strip(),
                self._current_timestamp(),
                snippet_id,
            ),
        )
        if cursor.rowcount == 0:
            self.connection.rollback()
            return None
        self._replace_snippet_tags(snippet_id, clean_tags)
        self.connection.commit()
        return self.get_snippet_by_id(snippet_id)

    def delete_snippet(self, snippet_id: int) -> bool:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM snippet_tags WHERE snippet_id = ?", (snippet_id,))
        cursor.execute("DELETE FROM code_snippets WHERE id = ?", (snippet_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def _replace_snippet_tags(self, snippet_id: int, tags: list[str]) -> None:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM snippet_tags WHERE snippet_id = ?", (snippet_id,))
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
                INSERT OR IGNORE INTO snippet_tags (snippet_id, tag_id)
                VALUES (?, ?)
                """,
                (snippet_id, tag_row["id"]),
            )

    def _build_snippet_query(self, where_clause: str = "") -> str:
        return f"""
            SELECT
                s.id,
                s.title,
                s.language,
                s.code,
                s.description,
                s.created_at,
                s.updated_at,
                COALESCE(GROUP_CONCAT(t.name, ','), '') AS tags
            FROM code_snippets s
            LEFT JOIN snippet_tags st ON st.snippet_id = s.id
            LEFT JOIN tags t ON t.id = st.tag_id
            {where_clause}
            GROUP BY s.id
            ORDER BY s.updated_at DESC, s.id DESC
        """

    def _map_row(self, row: sqlite3.Row) -> CodeSnippet:
        tags = [tag.strip() for tag in row["tags"].split(",") if tag.strip()]
        return CodeSnippet(
            id=row["id"],
            title=row["title"],
            language=row["language"],
            code=row["code"],
            description=row["description"],
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
            key = tag.casefold()
            if key in seen_tags:
                continue
            seen_tags.add(key)
            unique_tags.append(tag)
        return unique_tags

    def _current_timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
