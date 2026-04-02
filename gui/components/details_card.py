"""Details card for selected app."""

from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QLabel

from gui.components.material import MaterialCard


class DetailsCard(MaterialCard):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.display_name = QLabel("—")
        self.cmd = QLabel("—")
        self.match = QLabel("—")

        form = QFormLayout()
        form.setSpacing(12)
        form.addRow("Название", self.display_name)
        form.addRow("Команда", self.cmd)
        form.addRow("Окно", self.match)

        self.body.addLayout(form)
