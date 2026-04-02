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
    app.setQuitOnLastWindowClosed(False)

    app.setStyleSheet(
        """
        QWidget {
            background: #F5F5F5;
            color: #1F1F1F;
            font-size: 13px;
        }
        QToolBar {
            background: #EFEFEF;
            border-bottom: 1px solid #E0E0E0;
        }
        QListWidget, QPlainTextEdit, QComboBox, QLineEdit {
            background: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 6px;
            padding: 4px;
        }
        QPushButton {
            background: #FFFFFF;
            border: 1px solid #DADADA;
            border-radius: 6px;
            padding: 6px 10px;
        }
        QPushButton:hover {
            border-color: #3A86FF;
        }
        QListWidget::item:selected {
            background: #3A86FF;
            color: #FFFFFF;
        }
        QComboBox::drop-down {
            border: none;
        }
        """
    )

    icon_path = Path(__file__).resolve().parents[1] / "assets" / "icon.svg"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
