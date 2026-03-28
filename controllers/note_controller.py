from __future__ import annotations

from PyQt6.QtWidgets import QListWidgetItem, QMessageBox

from services.note_service import NoteService
from views.note_editor_dialog import NoteEditorDialog
from views.note_view import NoteView


class NoteController:
    def __init__(self, note_view: NoteView, note_service: NoteService, parent=None) -> None:
        self.note_view = note_view
        self.note_service = note_service
        self.parent = parent
        self._bind_events()
        self.load_notes()

    def _bind_events(self) -> None:
        self.note_view.create_button.clicked.connect(self.handle_create_note)
        self.note_view.edit_button.clicked.connect(self.handle_edit_note)
        self.note_view.delete_button.clicked.connect(self.handle_delete_note)
        self.note_view.search_button.clicked.connect(self.handle_search)
        self.note_view.reset_button.clicked.connect(self.handle_reset_search)
        self.note_view.search_input.returnPressed.connect(self.handle_search)
        self.note_view.note_list.itemSelectionChanged.connect(self.handle_note_selected)
        self.note_view.note_list.itemDoubleClicked.connect(self.handle_note_double_clicked)

    def load_notes(self, selected_note_id: int | None = None) -> None:
        notes = self.note_service.list_notes()
        self.note_view.populate_notes(notes)
        self.note_view.show_note_details(None)

        if not notes:
            return

        if selected_note_id is not None:
            self.note_view.select_note_by_id(selected_note_id)
            if self.note_view.current_note_id() is not None:
                self._show_current_note()
                return

        self.note_view.note_list.setCurrentRow(0)
        self._show_current_note()

    def handle_search(self) -> None:
        keyword = self.note_view.search_input.text().strip()
        if not keyword:
            self.load_notes()
            return

        notes = self.note_service.search_notes(keyword)
        self.note_view.populate_notes(notes)
        self.note_view.show_note_details(None)

        if notes:
            self.note_view.note_list.setCurrentRow(0)
            self._show_current_note()

    def handle_reset_search(self) -> None:
        self.note_view.search_input.clear()
        self.load_notes()

    def handle_create_note(self) -> None:
        dialog = NoteEditorDialog(self.parent)
        if dialog.exec() == NoteEditorDialog.DialogCode.Accepted:
            payload = dialog.get_payload()
            note = self.note_service.create_note(
                title=payload["title"],
                content=payload["content"],
                tags=payload["tags"],
            )
            self.load_notes(selected_note_id=note.id)
            self._show_information("筆記已成功新增。")

    def handle_edit_note(self) -> None:
        note_id = self.note_view.current_note_id()
        if note_id is None:
            self._show_warning("請先選擇要編輯的筆記。")
            return

        note = self.note_service.get_note_by_id(note_id)
        if note is None:
            self._show_warning("找不到這篇筆記，可能已被刪除。")
            self.load_notes()
            return

        dialog = NoteEditorDialog(self.parent, note=note)
        if dialog.exec() == NoteEditorDialog.DialogCode.Accepted:
            payload = dialog.get_payload()
            updated = self.note_service.update_note(
                note_id=note_id,
                title=payload["title"],
                content=payload["content"],
                tags=payload["tags"],
            )
            if updated is None:
                self._show_warning("更新失敗，請稍後再試。")
                return
            self.load_notes(selected_note_id=updated.id)
            self._show_information("筆記已成功更新。")

    def handle_delete_note(self) -> None:
        note_id = self.note_view.current_note_id()
        if note_id is None:
            self._show_warning("請先選擇要刪除的筆記。")
            return

        note = self.note_service.get_note_by_id(note_id)
        if note is None:
            self._show_warning("找不到這篇筆記，可能已被刪除。")
            self.load_notes()
            return

        reply = QMessageBox.question(
            self.parent,
            "確認刪除",
            f"確定要刪除筆記「{note.title}」嗎？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        deleted = self.note_service.delete_note(note_id)
        if deleted:
            self.load_notes()
            self._show_information("筆記已刪除。")
            return

        self._show_warning("刪除失敗，請稍後再試。")

    def handle_note_selected(self) -> None:
        self._show_current_note()

    def handle_note_double_clicked(self, item: QListWidgetItem) -> None:
        _ = item
        self.handle_edit_note()

    def _show_current_note(self) -> None:
        note_id = self.note_view.current_note_id()
        if note_id is None:
            self.note_view.show_note_details(None)
            return

        note = self.note_service.get_note_by_id(note_id)
        self.note_view.show_note_details(note)

    def _show_information(self, message: str) -> None:
        QMessageBox.information(self.parent, "技術筆記", message)

    def _show_warning(self, message: str) -> None:
        QMessageBox.warning(self.parent, "技術筆記", message)
