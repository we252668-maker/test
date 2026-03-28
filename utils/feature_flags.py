from __future__ import annotations

from dataclasses import dataclass

from utils import config


@dataclass(frozen=True)
class FeatureFlags:
    auth_enabled: bool = config.FEATURE_AUTH_ENABLED
    permission_control_enabled: bool = config.FEATURE_PERMISSION_CONTROL
    attachments_enabled: bool = config.FEATURE_ATTACHMENTS
    export_pdf_enabled: bool = config.FEATURE_EXPORT_PDF
    export_excel_enabled: bool = config.FEATURE_EXPORT_EXCEL
    full_text_search_enabled: bool = config.FEATURE_FULL_TEXT_SEARCH
    code_highlight_enabled: bool = config.FEATURE_CODE_HIGHLIGHT
    code_preview_enabled: bool = config.FEATURE_CODE_PREVIEW


def load_feature_flags() -> FeatureFlags:
    return FeatureFlags()
