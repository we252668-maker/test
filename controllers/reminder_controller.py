from __future__ import annotations

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QListWidgetItem, QMessageBox

from views.reminder_editor_dialog import ReminderEditorDialog
from views.scheduler_view import SchedulerView


TIMEOUT_MESSAGE = "\u96f2\u7aef\u670d\u52d9\u559a\u9192\u4e2d\uff0c\u8acb\u518d\u8a66\u4e00\u6b21"
LOADING_TEXT = "\u8f09\u5165\u4e2d..."


class ReminderController:
    def __init__(
        self,
        scheduler_view: SchedulerView,
        reminder_service,
        reminder_monitor_service,
        parent=None,
    ) -> None:
        self.scheduler_view = scheduler_view
        self.reminder_service = reminder_service
        self.reminder_monitor_service = reminder_monitor_service
        self.parent = parent
        self._bind_events()
        self.load_reminders()

    def _bind_events(self) -> None:
        self.scheduler_view.create_button.clicked.connect(self.handle_create_reminder)
        self.scheduler_view.edit_button.clicked.connect(self.handle_edit_reminder)
        self.scheduler_view.delete_button.clicked.connect(self.handle_delete_reminder)
        self.scheduler_view.search_button.clicked.connect(self.handle_search)
        self.scheduler_view.reset_button.clicked.connect(self.handle_reset_search)
        self.scheduler_view.search_input.returnPressed.connect(self.handle_search)
        self.scheduler_view.reminder_list.itemSelectionChanged.connect(self.handle_reminder_selected)
        self.scheduler_view.reminder_list.itemDoubleClicked.connect(self.handle_reminder_double_clicked)

    def load_reminders(self, selected_reminder_id: int | None = None) -> None:
        try:
            reminders = self._run_with_loading(self.reminder_service.list_reminders)
        except Exception as exc:
            self._show_api_error("Failed to load reminders.", exc)
            return

        self.scheduler_view.populate_reminders(reminders)
        self.scheduler_view.show_reminder_details(None)

        if not reminders:
            return
        if selected_reminder_id is not None:
            self.scheduler_view.select_reminder_by_id(selected_reminder_id)
            if self.scheduler_view.current_reminder_id() is not None:
                self._show_current_reminder()
                return
        self.scheduler_view.reminder_list.setCurrentRow(0)
        self._show_current_reminder()

    def handle_search(self) -> None:
        keyword = self.scheduler_view.search_input.text().strip()
        if not keyword:
            self.load_reminders()
            return

        try:
            reminders = self._run_with_loading(self.reminder_service.search_reminders, keyword)
        except Exception as exc:
            self._show_api_error("Failed to search reminders.", exc)
            return

        self.scheduler_view.populate_reminders(reminders)
        self.scheduler_view.show_reminder_details(None)
        if reminders:
            self.scheduler_view.reminder_list.setCurrentRow(0)
            self._show_current_reminder()

    def handle_reset_search(self) -> None:
        self.scheduler_view.search_input.clear()
        self.load_reminders()

    def handle_create_reminder(self) -> None:
        dialog = ReminderEditorDialog(self.parent)
        if dialog.exec() != ReminderEditorDialog.DialogCode.Accepted:
            return

        payload = dialog.get_payload()
        try:
            reminder = self._run_with_loading(self.reminder_service.create_reminder, **payload)
        except Exception as exc:
            self._show_api_error("Failed to create reminder.", exc)
            return

        self.reminder_monitor_service.send_creation_notice_async(reminder.id)
        self.load_reminders(selected_reminder_id=reminder.id)
        QMessageBox.information(self.parent, "Reminder", "Reminder created successfully.")

    def handle_edit_reminder(self) -> None:
        reminder_id = self.scheduler_view.current_reminder_id()
        if reminder_id is None:
            QMessageBox.warning(self.parent, "Reminder", "Please select a reminder first.")
            return

        try:
            reminder = self._run_with_loading(self.reminder_service.get_reminder_by_id, reminder_id)
        except Exception as exc:
            self._show_api_error("Failed to load reminder.", exc)
            return

        if reminder is None:
            QMessageBox.warning(self.parent, "Reminder", "The selected reminder no longer exists.")
            self.load_reminders()
            return

        dialog = ReminderEditorDialog(self.parent, reminder=reminder)
        if dialog.exec() != ReminderEditorDialog.DialogCode.Accepted:
            return

        payload = dialog.get_payload()
        try:
            updated = self._run_with_loading(
                self.reminder_service.update_reminder,
                reminder_id=reminder_id,
                **payload,
            )
        except Exception as exc:
            self._show_api_error("Failed to update reminder.", exc)
            return

        if updated is None:
            QMessageBox.warning(self.parent, "Reminder", "The reminder could not be updated.")
            return

        self.load_reminders(selected_reminder_id=updated.id)
        QMessageBox.information(self.parent, "Reminder", "Reminder updated successfully.")

    def handle_delete_reminder(self) -> None:
        reminder_id = self.scheduler_view.current_reminder_id()
        if reminder_id is None:
            QMessageBox.warning(self.parent, "Reminder", "Please select a reminder first.")
            return

        try:
            reminder = self._run_with_loading(self.reminder_service.get_reminder_by_id, reminder_id)
        except Exception as exc:
            self._show_api_error("Failed to load reminder.", exc)
            return

        if reminder is None:
            QMessageBox.warning(self.parent, "Reminder", "The selected reminder no longer exists.")
            self.load_reminders()
            return

        reply = QMessageBox.question(
            self.parent,
            "Delete Reminder",
            f"Delete reminder '{reminder.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            deleted = self._run_with_loading(self.reminder_service.delete_reminder, reminder_id)
        except Exception as exc:
            self._show_api_error("Failed to delete reminder.", exc)
            return

        if deleted:
            self.load_reminders()
            QMessageBox.information(self.parent, "Reminder", "Reminder deleted successfully.")
        else:
            QMessageBox.warning(self.parent, "Reminder", "The reminder could not be deleted.")

    def handle_reminder_selected(self) -> None:
        self._show_current_reminder()

    def handle_reminder_double_clicked(self, item: QListWidgetItem) -> None:
        _ = item
        self.handle_edit_reminder()

    def _show_current_reminder(self) -> None:
        reminder_id = self.scheduler_view.current_reminder_id()
        if reminder_id is None:
            self.scheduler_view.show_reminder_details(None)
            return

        try:
            reminder = self._run_with_loading(self.reminder_service.get_reminder_by_id, reminder_id)
        except Exception as exc:
            self._show_api_error("Failed to load reminder details.", exc)
            self.scheduler_view.show_reminder_details(None)
            return

        self.scheduler_view.show_reminder_details(reminder)

    def _show_api_error(self, message: str, exc: Exception) -> None:
        detail = self._extract_response_text(exc)
        text = message if not detail else f"{message}\n\n{detail}"
        QMessageBox.critical(self.parent, "API Error", text)

    def _extract_response_text(self, exc: Exception) -> str:
        if isinstance(exc, requests.Timeout):
            return TIMEOUT_MESSAGE
        response = getattr(exc, "response", None)
        if response is not None:
            try:
                return response.text.strip()
            except Exception:
                return str(exc)
        if isinstance(exc, requests.RequestException):
            return str(exc)
        return str(exc)

    def _run_with_loading(self, operation, *args, **kwargs):
        self._set_loading_state(True)
        try:
            return operation(*args, **kwargs)
        finally:
            self._set_loading_state(False)

    def _set_loading_state(self, is_loading: bool) -> None:
        self.scheduler_view.setCursor(Qt.CursorShape.WaitCursor if is_loading else Qt.CursorShape.ArrowCursor)
        self.scheduler_view.create_button.setDisabled(is_loading)
        self.scheduler_view.edit_button.setDisabled(is_loading)
        self.scheduler_view.delete_button.setDisabled(is_loading)
        self.scheduler_view.search_button.setDisabled(is_loading)
        self.scheduler_view.reset_button.setDisabled(is_loading)
        self.scheduler_view.search_input.setDisabled(is_loading)
        self.scheduler_view.reminder_list.setDisabled(is_loading)
        self.scheduler_view.setToolTip(LOADING_TEXT if is_loading else "")
        self.scheduler_view.repaint()
        QApplication.processEvents()
