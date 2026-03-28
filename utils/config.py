from __future__ import annotations

APP_NAME = "Engineer Hub"
DATABASE_FILE_NAME = "engineer_hub.db"
BASE_URL = "https://test-1-s4pq.onrender.com"
API_TIMEOUT_SECONDS = 30

# Feature flags reserved for commercial editions and staged rollout.
FEATURE_AUTH_ENABLED = False
FEATURE_PERMISSION_CONTROL = False
FEATURE_ATTACHMENTS = False
FEATURE_EXPORT_PDF = False
FEATURE_EXPORT_EXCEL = False
FEATURE_FULL_TEXT_SEARCH = False
FEATURE_CODE_HIGHLIGHT = False
FEATURE_CODE_PREVIEW = False

# Default desktop experience assumptions.
DEFAULT_WORKSPACE_NAME = "Personal Workspace"
DEFAULT_EXPORT_DIR_NAME = "exports"
DEFAULT_ATTACHMENT_DIR_NAME = "attachments"

# Gmail SMTP defaults for reminder emails.
SMTP_HOST = "smtp.gmail.com"
SMTP_SSL_PORT = 465
SMTP_DEFAULT_SENDER_NAME = APP_NAME
