from __future__ import annotations

from controllers.note_controller import NoteController
from controllers.reminder_controller import ReminderController
from controllers.search_controller import SearchController
from controllers.settings_controller import SettingsController
from controllers.snippet_controller import SnippetController
from database.connection import DatabaseManager
from services.attachment_service import AttachmentService
from services.auth_service import AuthService
from services.api_client import ApiClient
from services.noop_reminder_monitor_service import NoopReminderMonitorService
from services.export_service import ExportService
from services.note_service import NoteService
from services.permission_service import PermissionService
from services.remote_discord_service import RemoteDiscordService
from services.remote_reminder_service import RemoteReminderService
from services.search_service import SearchService
from services.snippet_service import SnippetService
from utils.config import BASE_URL
from utils.feature_flags import load_feature_flags
from views.main_window import MainWindow


class MainController:
    def __init__(self) -> None:
        self.database_manager = DatabaseManager()
        self.database_manager.initialize()

        connection = self.database_manager.get_connection()
        self.feature_flags = load_feature_flags()
        self.auth_service = AuthService(connection)
        self.session_context = self.auth_service.get_bootstrap_session()
        self.permission_service = PermissionService(connection)
        self.attachment_service = AttachmentService(connection)
        self.export_service = ExportService(connection)
        self.note_service = NoteService(connection)
        self.snippet_service = SnippetService(connection)
        self.search_service = SearchService(connection)
        self.api_base_url = BASE_URL
        api_client = ApiClient(self.api_base_url)
        self.discord_service = RemoteDiscordService(api_client)
        self.reminder_service = RemoteReminderService(api_client)
        self.reminder_monitor_service = NoopReminderMonitorService()

        self.main_window = MainWindow()
        self.settings_controller = SettingsController(
            discord_service=self.discord_service,
            parent=self.main_window,
        )
        self.reminder_controller = ReminderController(
            scheduler_view=self.main_window.scheduler_view,
            reminder_service=self.reminder_service,
            reminder_monitor_service=self.reminder_monitor_service,
            parent=self.main_window,
        )
        self.note_controller = NoteController(
            note_view=self.main_window.note_view,
            note_service=self.note_service,
            parent=self.main_window,
        )
        self.snippet_controller = SnippetController(
            snippet_view=self.main_window.snippet_view,
            snippet_service=self.snippet_service,
            parent=self.main_window,
        )
        self.search_controller = SearchController(
            search_view=self.main_window.search_view,
            search_service=self.search_service,
            main_window=self.main_window,
        )

        self.main_window.settings_action.triggered.connect(self.settings_controller.open_notification_settings)
        self.reminder_monitor_service.start()

    def show_main_window(self) -> None:
        self.main_window.show()

    def shutdown(self) -> None:
        self.reminder_monitor_service.stop()
