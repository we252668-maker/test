from __future__ import annotations

import sqlite3
from typing import Iterable


def initialize_database(connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL DEFAULT '',
            email TEXT NOT NULL DEFAULT '',
            password_hash TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'active',
            is_system_admin INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT ''
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT ''
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT ''
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_roles (
            user_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, role_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS role_permissions (
            role_id INTEGER NOT NULL,
            permission_id INTEGER NOT NULL,
            PRIMARY KEY (role_id, permission_id),
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
            FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT '一般',
            description TEXT DEFAULT '',
            due_at TEXT DEFAULT '',
            priority INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'pending',
            email_notification_enabled INTEGER NOT NULL DEFAULT 1,
            line_notification_enabled INTEGER NOT NULL DEFAULT 0,
            created_notice_sent_at TEXT NOT NULL DEFAULT '',
            reminder_notice_sent_at TEXT NOT NULL DEFAULT '',
            last_email_error TEXT NOT NULL DEFAULT '',
            line_notice_sent_at TEXT NOT NULL DEFAULT '',
            last_line_error TEXT NOT NULL DEFAULT '',
            discord_creation_notice_sent_at TEXT NOT NULL DEFAULT '',
            discord_due_notice_sent_at TEXT NOT NULL DEFAULT '',
            last_discord_error TEXT NOT NULL DEFAULT '',
            owner_id INTEGER,
            created_by INTEGER,
            updated_by INTEGER,
            created_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (owner_id) REFERENCES users(id),
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (updated_by) REFERENCES users(id)
        )
        """
    )
    _ensure_columns(
        connection,
        table_name="reminders",
        required_columns=(
            ("category", "TEXT NOT NULL DEFAULT '一般'"),
            ("priority", "INTEGER NOT NULL DEFAULT 0"),
            ("email_notification_enabled", "INTEGER NOT NULL DEFAULT 1"),
            ("line_notification_enabled", "INTEGER NOT NULL DEFAULT 0"),
            ("created_notice_sent_at", "TEXT NOT NULL DEFAULT ''"),
            ("reminder_notice_sent_at", "TEXT NOT NULL DEFAULT ''"),
            ("last_email_error", "TEXT NOT NULL DEFAULT ''"),
            ("line_notice_sent_at", "TEXT NOT NULL DEFAULT ''"),
            ("last_line_error", "TEXT NOT NULL DEFAULT ''"),
            ("discord_creation_notice_sent_at", "TEXT NOT NULL DEFAULT ''"),
            ("discord_due_notice_sent_at", "TEXT NOT NULL DEFAULT ''"),
            ("last_discord_error", "TEXT NOT NULL DEFAULT ''"),
            ("owner_id", "INTEGER"),
            ("created_by", "INTEGER"),
            ("updated_by", "INTEGER"),
            ("created_at", "TEXT NOT NULL DEFAULT ''"),
            ("updated_at", "TEXT NOT NULL DEFAULT ''"),
        ),
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL DEFAULT '',
            summary TEXT DEFAULT '',
            owner_id INTEGER,
            created_by INTEGER,
            updated_by INTEGER,
            created_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (owner_id) REFERENCES users(id),
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (updated_by) REFERENCES users(id)
        )
        """
    )
    _ensure_columns(
        connection,
        table_name="notes",
        required_columns=(
            ("summary", "TEXT DEFAULT ''"),
            ("owner_id", "INTEGER"),
            ("created_by", "INTEGER"),
            ("updated_by", "INTEGER"),
            ("created_at", "TEXT NOT NULL DEFAULT ''"),
            ("updated_at", "TEXT NOT NULL DEFAULT ''"),
        ),
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS note_tags (
            note_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (note_id, tag_id),
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS code_snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            language TEXT NOT NULL DEFAULT 'python',
            code TEXT NOT NULL DEFAULT '',
            description TEXT DEFAULT '',
            owner_id INTEGER,
            created_by INTEGER,
            updated_by INTEGER,
            renderer_type TEXT NOT NULL DEFAULT 'plain_text',
            preview_payload TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (owner_id) REFERENCES users(id),
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (updated_by) REFERENCES users(id)
        )
        """
    )
    _ensure_columns(
        connection,
        table_name="code_snippets",
        required_columns=(
            ("description", "TEXT DEFAULT ''"),
            ("owner_id", "INTEGER"),
            ("created_by", "INTEGER"),
            ("updated_by", "INTEGER"),
            ("renderer_type", "TEXT NOT NULL DEFAULT 'plain_text'"),
            ("preview_payload", "TEXT NOT NULL DEFAULT ''"),
            ("created_at", "TEXT NOT NULL DEFAULT ''"),
            ("updated_at", "TEXT NOT NULL DEFAULT ''"),
        ),
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS snippet_tags (
            snippet_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (snippet_id, tag_id),
            FOREIGN KEY (snippet_id) REFERENCES code_snippets(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS email_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            gmail_address TEXT NOT NULL DEFAULT '',
            app_password TEXT NOT NULL DEFAULT '',
            sender_name TEXT NOT NULL DEFAULT '',
            recipient_email TEXT NOT NULL DEFAULT '',
            is_enabled INTEGER NOT NULL DEFAULT 0,
            line_notify_token TEXT NOT NULL DEFAULT '',
            line_notify_enabled INTEGER NOT NULL DEFAULT 0,
            discord_webhook_url TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT ''
        )
        """
    )
    _ensure_columns(
        connection,
        table_name="email_settings",
        required_columns=(
            ("line_notify_token", "TEXT NOT NULL DEFAULT ''"),
            ("line_notify_enabled", "INTEGER NOT NULL DEFAULT 0"),
            ("discord_webhook_url", "TEXT NOT NULL DEFAULT ''"),
        ),
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_type TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            stored_path TEXT NOT NULL,
            mime_type TEXT NOT NULL DEFAULT '',
            file_size INTEGER NOT NULL DEFAULT 0,
            checksum TEXT NOT NULL DEFAULT '',
            created_by INTEGER,
            created_at TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS export_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            export_type TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source_id INTEGER,
            file_path TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'pending',
            requested_by INTEGER,
            requested_at TEXT NOT NULL DEFAULT '',
            completed_at TEXT NOT NULL DEFAULT '',
            error_message TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (requested_by) REFERENCES users(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS search_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,
            source_id INTEGER NOT NULL,
            title TEXT NOT NULL DEFAULT '',
            content TEXT NOT NULL DEFAULT '',
            tags_text TEXT NOT NULL DEFAULT '',
            owner_id INTEGER,
            updated_at TEXT NOT NULL DEFAULT '',
            UNIQUE(source_type, source_id),
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_users_username
        ON users(username)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_roles_code
        ON roles(code)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_permissions_code
        ON permissions(code)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_reminders_due_at
        ON reminders(due_at)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_reminders_owner_id
        ON reminders(owner_id)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_notes_updated_at
        ON notes(updated_at)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_notes_owner_id
        ON notes(owner_id)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_code_snippets_updated_at
        ON code_snippets(updated_at)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_code_snippets_owner_id
        ON code_snippets(owner_id)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_tags_name
        ON tags(name)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_note_tags_note_id
        ON note_tags(note_id)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_note_tags_tag_id
        ON note_tags(tag_id)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_snippet_tags_snippet_id
        ON snippet_tags(snippet_id)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_snippet_tags_tag_id
        ON snippet_tags(tag_id)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_reminders_email_due
        ON reminders(status, email_notification_enabled, reminder_notice_sent_at, due_at)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_reminders_line_due
        ON reminders(status, line_notification_enabled, line_notice_sent_at, due_at)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_reminders_discord_due
        ON reminders(status, discord_due_notice_sent_at, due_at)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_attachments_owner
        ON attachments(owner_type, owner_id)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_export_jobs_status
        ON export_jobs(status)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_search_documents_source
        ON search_documents(source_type, source_id)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_search_documents_owner
        ON search_documents(owner_id)
        """
    )

    _seed_default_security_data(connection)
    connection.commit()


def _seed_default_security_data(connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()
    permissions = (
        ("note.read", "Read notes"),
        ("note.write", "Write notes"),
        ("reminder.read", "Read reminders"),
        ("reminder.write", "Write reminders"),
        ("snippet.read", "Read snippets"),
        ("snippet.write", "Write snippets"),
        ("search.global", "Use global search"),
        ("attachment.manage", "Manage attachments"),
        ("export.data", "Export business data"),
        ("admin.system", "System administration"),
    )
    roles = (
        ("admin", "Administrator"),
        ("editor", "Editor"),
        ("viewer", "Viewer"),
    )
    for code, name in permissions:
        cursor.execute(
            """
            INSERT INTO permissions (code, name)
            VALUES (?, ?)
            ON CONFLICT(code) DO NOTHING
            """,
            (code, name),
        )
    for code, name in roles:
        cursor.execute(
            """
            INSERT INTO roles (code, name)
            VALUES (?, ?)
            ON CONFLICT(code) DO NOTHING
            """,
            (code, name),
        )


def _ensure_columns(
    connection: sqlite3.Connection,
    table_name: str,
    required_columns: Iterable[tuple[str, str]],
) -> None:
    cursor = connection.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = {row[1] for row in cursor.fetchall()}

    for column_name, column_definition in required_columns:
        if column_name in existing_columns:
            continue
        cursor.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        )
