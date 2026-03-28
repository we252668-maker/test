from __future__ import annotations

from PyQt6.QtWidgets import QListWidgetItem, QMessageBox

from services.snippet_service import SnippetService
from views.snippet_editor_dialog import SnippetEditorDialog
from views.snippet_view import SnippetView


class SnippetController:
    def __init__(self, snippet_view: SnippetView, snippet_service: SnippetService, parent=None) -> None:
        self.snippet_view = snippet_view
        self.snippet_service = snippet_service
        self.parent = parent
        self._bind_events()
        self.load_snippets()

    def _bind_events(self) -> None:
        self.snippet_view.create_button.clicked.connect(self.handle_create_snippet)
        self.snippet_view.edit_button.clicked.connect(self.handle_edit_snippet)
        self.snippet_view.delete_button.clicked.connect(self.handle_delete_snippet)
        self.snippet_view.search_button.clicked.connect(self.handle_search)
        self.snippet_view.reset_button.clicked.connect(self.handle_reset_search)
        self.snippet_view.search_input.returnPressed.connect(self.handle_search)
        self.snippet_view.snippet_list.itemSelectionChanged.connect(self.handle_snippet_selected)
        self.snippet_view.snippet_list.itemDoubleClicked.connect(self.handle_snippet_double_clicked)

    def load_snippets(self, selected_snippet_id: int | None = None) -> None:
        snippets = self.snippet_service.list_snippets()
        self.snippet_view.populate_snippets(snippets)
        self.snippet_view.show_snippet_details(None)
        if not snippets:
            return
        if selected_snippet_id is not None:
            self.snippet_view.select_snippet_by_id(selected_snippet_id)
            if self.snippet_view.current_snippet_id() is not None:
                self._show_current_snippet()
                return
        self.snippet_view.snippet_list.setCurrentRow(0)
        self._show_current_snippet()

    def handle_search(self) -> None:
        keyword = self.snippet_view.search_input.text().strip()
        if not keyword:
            self.load_snippets()
            return
        snippets = self.snippet_service.search_snippets(keyword)
        self.snippet_view.populate_snippets(snippets)
        self.snippet_view.show_snippet_details(None)
        if snippets:
            self.snippet_view.snippet_list.setCurrentRow(0)
            self._show_current_snippet()

    def handle_reset_search(self) -> None:
        self.snippet_view.search_input.clear()
        self.load_snippets()

    def handle_create_snippet(self) -> None:
        dialog = SnippetEditorDialog(self.parent)
        if dialog.exec() == SnippetEditorDialog.DialogCode.Accepted:
            payload = dialog.get_payload()
            snippet = self.snippet_service.create_snippet(**payload)
            self.load_snippets(selected_snippet_id=snippet.id)
            QMessageBox.information(self.parent, "程式碼片段", "程式碼片段已成功新增。")

    def handle_edit_snippet(self) -> None:
        snippet_id = self.snippet_view.current_snippet_id()
        if snippet_id is None:
            QMessageBox.warning(self.parent, "程式碼片段", "請先選擇要編輯的程式碼片段。")
            return

        snippet = self.snippet_service.get_snippet_by_id(snippet_id)
        if snippet is None:
            QMessageBox.warning(self.parent, "程式碼片段", "找不到這筆程式碼片段。")
            self.load_snippets()
            return

        dialog = SnippetEditorDialog(self.parent, snippet=snippet)
        if dialog.exec() == SnippetEditorDialog.DialogCode.Accepted:
            payload = dialog.get_payload()
            updated = self.snippet_service.update_snippet(snippet_id=snippet_id, **payload)
            if updated is None:
                QMessageBox.warning(self.parent, "程式碼片段", "更新失敗，請稍後再試。")
                return
            self.load_snippets(selected_snippet_id=updated.id)
            QMessageBox.information(self.parent, "程式碼片段", "程式碼片段已成功更新。")

    def handle_delete_snippet(self) -> None:
        snippet_id = self.snippet_view.current_snippet_id()
        if snippet_id is None:
            QMessageBox.warning(self.parent, "程式碼片段", "請先選擇要刪除的程式碼片段。")
            return

        snippet = self.snippet_service.get_snippet_by_id(snippet_id)
        if snippet is None:
            QMessageBox.warning(self.parent, "程式碼片段", "找不到這筆程式碼片段。")
            self.load_snippets()
            return

        reply = QMessageBox.question(
            self.parent,
            "確認刪除",
            f"確定要刪除程式碼片段「{snippet.title}」嗎？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        if self.snippet_service.delete_snippet(snippet_id):
            self.load_snippets()
            QMessageBox.information(self.parent, "程式碼片段", "程式碼片段已刪除。")
        else:
            QMessageBox.warning(self.parent, "程式碼片段", "刪除失敗，請稍後再試。")

    def handle_snippet_selected(self) -> None:
        self._show_current_snippet()

    def handle_snippet_double_clicked(self, item: QListWidgetItem) -> None:
        _ = item
        self.handle_edit_snippet()

    def _show_current_snippet(self) -> None:
        snippet_id = self.snippet_view.current_snippet_id()
        if snippet_id is None:
            self.snippet_view.show_snippet_details(None)
            return
        snippet = self.snippet_service.get_snippet_by_id(snippet_id)
        self.snippet_view.show_snippet_details(snippet)
