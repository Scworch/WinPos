"""GUI entry point."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtGui import QFont, QFontDatabase, QIcon
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setOrganizationName("Scworch")
    app.setApplicationName("WinPos")
    app.setQuitOnLastWindowClosed(False)

    font_family = "Inter" if "Inter" in QFontDatabase.families() else "Segoe UI"
    app.setFont(QFont(font_family, 12))

    app.setStyleSheet(
        """
        QWidget {
            background: #FFFBFE;
            color: #1C1B1F;
        }
        #Toolbar {
            background: #FFFFFF;
            border-bottom: 1px solid #E7E0EC;
            border-radius: 0px;
        }
        #MaterialCard {
            background: transparent;
        }
        #CardSurface {
            background: #FFFFFF;
            border: 1px solid #E7E0EC;
            border-radius: 24px;
        }
        QListWidget, QPlainTextEdit {
            background: #FFFFFF;
            border: 1px solid #E7E0EC;
            border-radius: 18px;
            padding: 6px;
        }
        QLineEdit, QComboBox {
            background: #FFFFFF;
            border: none;
            border-bottom: 2px solid #CAC4D0;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            padding: 6px 8px;
        }
        QLineEdit:focus, QComboBox:focus {
            border-bottom: 2px solid #3A86FF;
        }
        QPushButton {
            background: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 12px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background: #F6F6F6;
        }
        QPushButton:pressed {
            background: #EFEFEF;
        }
        QToolTip {
            background: #1C1B1F;
            color: #FFFFFF;
            border-radius: 6px;
            padding: 4px 6px;
        }
        #MaterialButton {
            border-radius: 9999px;
            padding: 8px 16px;
        }
        #MaterialButton:hover {
            background: #F1F5FF;
            border-color: #3A86FF;
        }
        #MaterialButton:pressed {
            background: #E0EAFF;
        }
        QListWidget::item:selected {
            background: #3A86FF;
            color: #FFFFFF;
        }
        QComboBox::drop-down {
            border: none;
        }
        QLabel#PanelTitle {
            font-size: 14px;
            font-weight: 600;
        }
        """
    )

    icon_path = ROOT / "assets" / "icon.svg"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
