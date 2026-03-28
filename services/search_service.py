from __future__ import annotations

import sqlite3

from models.search_result import SearchResult
from services.search_provider import SearchProvider


class SearchService(SearchProvider):
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def search(self, keyword: str) -> list[SearchResult]:
        normalized = f"%{keyword.strip()}%"
        results: list[SearchResult] = []

        results.extend(self._search_reminders(normalized))
        results.extend(self._search_notes(normalized))
        results.extend(self._search_snippets(normalized))

        results.sort(key=lambda item: (item.source_type, item.title.casefold()))
        return results

    def _search_reminders(self, normalized: str) -> list[SearchResult]:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT id, title, category, description, due_at, status
            FROM reminders
            WHERE title LIKE ? OR category LIKE ? OR description LIKE ? OR due_at LIKE ?
            ORDER BY due_at ASC, id DESC
            """,
            (normalized, normalized, normalized, normalized),
        )
        return [
            SearchResult(
                source_type="提醒事項",
                source_id=row["id"],
                title=row["title"],
                subtitle=(
                    f"分類：{row['category']} | 時間：{row['due_at'] or '-'} | "
                    f"狀態：{self._translate_status(row['status'])}"
                ),
                content_preview=row["description"] or "",
            )
            for row in cursor.fetchall()
        ]

    def _search_notes(self, normalized: str) -> list[SearchResult]:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT
                n.id,
                n.title,
                n.content,
                COALESCE(GROUP_CONCAT(t.name, ','), '') AS tags
            FROM notes n
            LEFT JOIN note_tags nt ON nt.note_id = n.id
            LEFT JOIN tags t ON t.id = nt.tag_id
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
            GROUP BY n.id
            ORDER BY n.updated_at DESC, n.id DESC
            """,
            {"keyword": normalized},
        )
        return [
            SearchResult(
                source_type="技術筆記",
                source_id=row["id"],
                title=row["title"],
                subtitle="研發心得 / 技術筆記",
                content_preview=self._compact_text(row["content"]),
                tags_text=row["tags"],
            )
            for row in cursor.fetchall()
        ]

    def _search_snippets(self, normalized: str) -> list[SearchResult]:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT
                s.id,
                s.title,
                s.language,
                s.code,
                s.description,
                COALESCE(GROUP_CONCAT(t.name, ','), '') AS tags
            FROM code_snippets s
            LEFT JOIN snippet_tags st ON st.snippet_id = s.id
            LEFT JOIN tags t ON t.id = st.tag_id
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
            GROUP BY s.id
            ORDER BY s.updated_at DESC, s.id DESC
            """,
            {"keyword": normalized},
        )
        return [
            SearchResult(
                source_type="程式碼片段",
                source_id=row["id"],
                title=row["title"],
                subtitle=f"語言：{row['language']}",
                content_preview=self._compact_text(row["description"] or row["code"]),
                tags_text=row["tags"],
            )
            for row in cursor.fetchall()
        ]

    def _compact_text(self, text: str, limit: int = 140) -> str:
        compact = " ".join(text.split())
        if len(compact) <= limit:
            return compact
        return f"{compact[:limit].rstrip()}..."

    def _translate_status(self, status: str) -> str:
        mapping = {
            "pending": "待處理",
            "done": "已完成",
            "cancelled": "已取消",
        }
        return mapping.get(status, status)
