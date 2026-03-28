from __future__ import annotations

from PyQt6.QtWidgets import QMessageBox

from services.search_service import SearchService
from views.main_window import MainWindow
from views.search_view import SearchView


class SearchController:
    def __init__(self, search_view: SearchView, search_service: SearchService, main_window: MainWindow) -> None:
        self.search_view = search_view
        self.search_service = search_service
        self.main_window = main_window
        self._bind_events()

    def _bind_events(self) -> None:
        self.search_view.search_button.clicked.connect(self.handle_search)
        self.search_view.reset_button.clicked.connect(self.handle_reset)
        self.search_view.open_button.clicked.connect(self.handle_open_source)
        self.search_view.search_input.returnPressed.connect(self.handle_search)
        self.search_view.results_list.itemSelectionChanged.connect(self.handle_result_selected)
        self.search_view.results_list.itemDoubleClicked.connect(lambda _: self.handle_open_source())

    def handle_search(self) -> None:
        keyword = self.search_view.search_input.text().strip()
        if not keyword:
            self.handle_reset()
            return

        results = self.search_service.search(keyword)
        self.search_view.populate_results(results)
        self.main_window.statusBar().showMessage(f"搜尋完成，共找到 {len(results)} 筆結果")
        if results:
            self.search_view.results_list.setCurrentRow(0)
            self.search_view.show_result_details(self.search_view.current_result())
        else:
            self.search_view.show_result_details(None)

    def handle_reset(self) -> None:
        self.search_view.search_input.clear()
        self.search_view.populate_results([])
        self.search_view.show_result_details(None)
        self.main_window.statusBar().showMessage("系統已就緒")

    def handle_result_selected(self) -> None:
        self.search_view.show_result_details(self.search_view.current_result())

    def handle_open_source(self) -> None:
        result = self.search_view.current_result()
        if result is None:
            QMessageBox.information(self.main_window, "全域搜尋", "請先選擇一筆搜尋結果。")
            return

        if result.source_type == "提醒事項":
            self.main_window.tab_widget.setCurrentWidget(self.main_window.scheduler_view)
            self.main_window.scheduler_view.select_reminder_by_id(result.source_id)
            self.main_window.scheduler_view.reminder_list.setFocus()
        elif result.source_type == "技術筆記":
            self.main_window.tab_widget.setCurrentWidget(self.main_window.note_view)
            self.main_window.note_view.select_note_by_id(result.source_id)
            self.main_window.note_view.note_list.setFocus()
        elif result.source_type == "程式碼片段":
            self.main_window.tab_widget.setCurrentWidget(self.main_window.snippet_view)
            self.main_window.snippet_view.select_snippet_by_id(result.source_id)
            self.main_window.snippet_view.snippet_list.setFocus()

        self.main_window.statusBar().showMessage(f"已前往來源：{result.title}")
