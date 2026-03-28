from __future__ import annotations

import sys

from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication

from controllers.main_controller import MainController


def main() -> int:
    load_dotenv()
    app = QApplication(sys.argv)
    controller = MainController()
    app.aboutToQuit.connect(controller.shutdown)
    controller.show_main_window()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
