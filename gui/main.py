"""GUI entry point."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setOrganizationName("Scworch")
    app.setApplicationName("WinPos")

    app.setStyleSheet(
        \"\"\"\n        QWidget {\n            background: #F5F5F5;\n            color: #1F1F1F;\n            font-size: 13px;\n        }\n        QToolBar {\n            background: #EFEFEF;\n            border-bottom: 1px solid #E0E0E0;\n        }\n        QListWidget, QPlainTextEdit, QComboBox, QLineEdit {\n            background: #FFFFFF;\n            border: 1px solid #E0E0E0;\n            border-radius: 6px;\n            padding: 4px;\n        }\n        QPushButton {\n            background: #FFFFFF;\n            border: 1px solid #DADADA;\n            border-radius: 6px;\n            padding: 6px 10px;\n        }\n        QPushButton:hover {\n            border-color: #3A86FF;\n        }\n        QListWidget::item:selected {\n            background: #3A86FF;\n            color: #FFFFFF;\n        }\n        QComboBox::drop-down {\n            border: none;\n        }\n        \"\"\"\n    )

    icon_path = Path(__file__).resolve().parents[1] / "assets" / "icon.svg"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
