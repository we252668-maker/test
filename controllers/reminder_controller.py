from __future__ import annotations

from PyQt6.QtWidgets import QListWidgetItem, QMessageBox

from services.reminder_monitor_service import ReminderMonitorService
from services.reminder_service import ReminderService
from views.reminder_editor_dialog import ReminderEditorDialog
from views.scheduler_view import SchedulerView


class ReminderController:
    def __init__(
        self,
        scheduler_view: SchedulerView,
        reminder_service: ReminderService,
        reminder_monitor_service: ReminderMonitorService,
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
        reminders = self.reminder_service.list_reminders()
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
        reminders = self.reminder_service.search_reminders(keyword)
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
        if dialog.exec() == ReminderEditorDialog.DialogCode.Accepted:
            payload = dialog.get_payload()
            reminder = self.reminder_service.create_reminder(**payload)
            self.reminder_monitor_service.send_creation_notice_async(reminder.id)
            self.load_reminders(selected_reminder_id=reminder.id)
            QMessageBox.information(
                self.parent,
                "提醒已建立",
                "提醒已儲存，系統會依設定自動發送建立通知與到期通知。",
            )

    def handle_edit_reminder(self) -> None:
        reminder_id = self.scheduler_view.current_reminder_id()
        if reminder_id is None:
            QMessageBox.warning(self.parent, "提醒管理", "請先選擇要編輯的提醒。")
            return

        reminder = self.reminder_service.get_reminder_by_id(reminder_id)
        if reminder is None:
            QMessageBox.warning(self.parent, "提醒管理", "找不到指定提醒。")
            self.load_reminders()
            return

        dialog = ReminderEditorDialog(self.parent, reminder=reminder)
        if dialog.exec() == ReminderEditorDialog.DialogCode.Accepted:
            payload = dialog.get_payload()
            updated = self.reminder_service.update_reminder(reminder_id=reminder_id, **payload)
            if updated is None:
                QMessageBox.warning(self.parent, "提醒管理", "更新失敗，請再試一次。")
                return
            self.load_reminders(selected_reminder_id=updated.id)
            QMessageBox.information(self.parent, "提醒管理", "提醒已更新。")

    def handle_delete_reminder(self) -> None:
        reminder_id = self.scheduler_view.current_reminder_id()
        if reminder_id is None:
            QMessageBox.warning(self.parent, "提醒管理", "請先選擇要刪除的提醒。")
            return

        reminder = self.reminder_service.get_reminder_by_id(reminder_id)
        if reminder is None:
            QMessageBox.warning(self.parent, "提醒管理", "找不到指定提醒。")
            self.load_reminders()
            return

        reply = QMessageBox.question(
            self.parent,
            "刪除提醒",
            f"確定要刪除「{reminder.title}」嗎？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        if self.reminder_service.delete_reminder(reminder_id):
            self.load_reminders()
            QMessageBox.information(self.parent, "提醒管理", "提醒已刪除。")
        else:
            QMessageBox.warning(self.parent, "提醒管理", "刪除失敗，請再試一次。")

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
        reminder = self.reminder_service.get_reminder_by_id(reminder_id)
        self.scheduler_view.show_reminder_details(reminder)
