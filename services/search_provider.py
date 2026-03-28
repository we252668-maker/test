from __future__ import annotations

from typing import Protocol

from models.search_result import SearchResult


class SearchProvider(Protocol):
    def search(self, keyword: str) -> list[SearchResult]:
        ...
