from __future__ import annotations

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QStatusBar, QTabWidget

from views.note_view import NoteView
from views.scheduler_view import SchedulerView
from views.search_view import SearchView
from views.snippet_view import SnippetView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Engineer Hub")
        self.resize(1280, 800)

        self.tab_widget = QTabWidget()
        self.scheduler_view = SchedulerView()
        self.note_view = NoteView()
        self.snippet_view = SnippetView()
        self.search_view = SearchView()

        self.tab_widget.addTab(self.scheduler_view, "提醒事項")
        self.tab_widget.addTab(self.note_view, "筆記")
        self.tab_widget.addTab(self.snippet_view, "程式片段")
        self.tab_widget.addTab(self.search_view, "搜尋")

        self.settings_action = QAction("通知設定", self)
        settings_menu = self.menuBar().addMenu("設定")
        settings_menu.addAction(self.settings_action)

        self.setCentralWidget(self.tab_widget)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("系統已就緒")
