from __future__ import annotations

import sys
from pathlib import Path

from utils.config import DATABASE_FILE_NAME


def _get_bundle_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def _get_app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


BUNDLE_DIR = _get_bundle_dir()
APP_DIR = _get_app_dir()
DATA_DIR = APP_DIR / "data"


def ensure_data_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def resource_path(*parts: str) -> Path:
    return BUNDLE_DIR.joinpath(*parts)


def get_bundled_database_path() -> Path:
    return resource_path("data", DATABASE_FILE_NAME)


def get_database_path() -> Path:
    return ensure_data_dir() / DATABASE_FILE_NAME
