from __future__ import annotations

import sqlite3
from shutil import copy2
from pathlib import Path

from database.init_db import initialize_database
from utils.paths import ensure_data_dir, get_bundled_database_path, get_database_path


class DatabaseManager:
    def __init__(self, database_path: Path | None = None) -> None:
        ensure_data_dir()
        self.database_path = database_path or get_database_path()
        self._ensure_seed_database()
        self._connection: sqlite3.Connection | None = None

    def _ensure_seed_database(self) -> None:
        if self.database_path.exists():
            return

        bundled_database_path = get_bundled_database_path()
        if bundled_database_path.exists() and bundled_database_path != self.database_path:
            copy2(bundled_database_path, self.database_path)

    def initialize(self) -> None:
        connection = self.get_connection()
        initialize_database(connection)

    def get_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = open_database_connection(self.database_path)
        return self._connection


def open_database_connection(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection
