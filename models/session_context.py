from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SessionContext:
    user_id: int | None = None
    username: str = "local_user"
    display_name: str = "Local User"
    workspace_id: int | None = None
    workspace_name: str = "Personal Workspace"
    is_authenticated: bool = False
    is_system_admin: bool = True
