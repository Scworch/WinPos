"""GUI dialogs for WinPos."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import yaml
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
)


ACTION_TYPES = [
    "launch_app",
    "wait_for_process",
    "wait_for_window",
    "bring_to_foreground",
    "move_window_to_monitor",
    "center_window",
    "resize_window",
    "maximize",
    "minimize",
    "send_hotkeys",
    "send_text",
    "open_url",
    "wait_for_title_change",
    "wait_for_visibility",
    "use_chain",
]


class AppDialog(QDialog):
    def __init__(self, app_id: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> None:
        super().__init__()
        self.setWindowTitle("Приложение")
        self._data = data or {}
        self._window_cache: List[Any] = []

        self.app_id_edit = QLineEdit(app_id or "")
        self.display_name_edit = QLineEdit(self._data.get("display_name", ""))
        self.cmd_edit = QLineEdit(self._data.get("launch", {}).get("cmd", ""))
        self.args_edit = QLineEdit(",".join(self._data.get("launch", {}).get("args", []) or [])
        )
        self.cwd_edit = QLineEdit(self._data.get("launch", {}).get("cwd", ""))
        match = self._data.get("window_match", {})
        self.title_contains_edit = QLineEdit(match.get("title_contains", ""))
        self.title_equals_edit = QLineEdit(match.get("title_equals", ""))
        self.class_name_edit = QLineEdit(match.get("class_name", ""))
        self.process_name_edit = QLineEdit(match.get("process_name", ""))

        self.window_combo = QComboBox()
        self.refresh_windows_btn = QPushButton("Обновить окна")
        self.apply_window_btn = QPushButton("Заполнить из окна")
        self.refresh_windows_btn.clicked.connect(self._refresh_windows)
        self.apply_window_btn.clicked.connect(self._apply_window_selection)

        form = QFormLayout()
        form.addRow("ID", self.app_id_edit)
        form.addRow("Название", self.display_name_edit)
        form.addRow("Команда", self.cmd_edit)
        form.addRow("Аргументы (через ,)", self.args_edit)
        form.addRow("Рабочая папка", self.cwd_edit)
        form.addRow("Заголовок содержит", self.title_contains_edit)
        form.addRow("Заголовок равен", self.title_equals_edit)
        form.addRow("Класс окна", self.class_name_edit)
        form.addRow("Имя процесса", self.process_name_edit)

        window_row = QHBoxLayout()
        window_row.addWidget(self.window_combo)
        window_row.addWidget(self.refresh_windows_btn)
        window_row.addWidget(self.apply_window_btn)
        form.addRow("Запущенные окна", window_row)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

        if app_id:
            self.app_id_edit.setDisabled(True)
        self._refresh_windows()

    def _refresh_windows(self) -> None:
        self.window_combo.clear()
        self._window_cache = []
        try:
            from windows.window_manager import WindowManager
        except Exception:
            self.window_combo.addItem("Не удалось получить окна")
            return
        manager = WindowManager()
        windows = manager.list_windows()
        for win in windows:
            label = f"{win.title} [{win.class_name}]"
            self.window_combo.addItem(label, win)
            self._window_cache.append(win)

    def _apply_window_selection(self) -> None:
        data = self.window_combo.currentData()
        if not data:
            return
        title = getattr(data, "title", "")
        class_name = getattr(data, "class_name", "")
        if title:
            self.title_contains_edit.setText(title)
        if class_name:
            self.class_name_edit.setText(class_name)

    def get_data(self) -> Optional[Dict[str, Any]]:
        if self.exec() != QDialog.Accepted:
            return None
        app_id = self.app_id_edit.text().strip()
        if not app_id:
            QMessageBox.warning(self, "Ошибка", "ID приложения обязателен")
            return None
        args = [arg.strip() for arg in self.args_edit.text().split(",") if arg.strip()]
        data = {
            "display_name": self.display_name_edit.text().strip() or app_id,
            "launch": {
                "cmd": self.cmd_edit.text().strip(),
                "args": args,
                "cwd": self.cwd_edit.text().strip() or None,
            },
            "window_match": {
                "title_contains": self.title_contains_edit.text().strip() or None,
                "title_equals": self.title_equals_edit.text().strip() or None,
                "class_name": self.class_name_edit.text().strip() or None,
                "process_name": self.process_name_edit.text().strip() or None,
            },
            "actions": self._data.get("actions", []),
        }
        data["launch"] = {k: v for k, v in data["launch"].items() if v}
        data["window_match"] = {k: v for k, v in data["window_match"].items() if v}
        return {"app_id": app_id, "data": data}


class ActionDialog(QDialog):
    def __init__(self, action: Optional[Dict[str, Any]] = None) -> None:
        super().__init__()
        self.setWindowTitle("Действие")
        action = action or {}

        self.type_combo = QComboBox()
        self.type_combo.addItems(ACTION_TYPES)
        if action.get("type"):
            index = self.type_combo.findText(action["type"])
            if index >= 0:
                self.type_combo.setCurrentIndex(index)

        self.params_edit = QPlainTextEdit()
        self.params_edit.setPlaceholderText("params: { key: value }")
        self.params_edit.setPlainText(_dump_yaml(action.get("params")))

        self.when_edit = QPlainTextEdit()
        self.when_edit.setPlaceholderText("when: { type: process_running }")
        self.when_edit.setPlainText(_dump_yaml(action.get("when")))

        self.retry_edit = QPlainTextEdit()
        self.retry_edit.setPlaceholderText("retry: { retries: 2, delay_s: 0.5 }")
        self.retry_edit.setPlainText(_dump_yaml(action.get("retry")))

        self.on_failure_edit = QPlainTextEdit()
        self.on_failure_edit.setPlaceholderText("- type: minimize")
        self.on_failure_edit.setPlainText(_dump_yaml(action.get("on_failure")))

        form = QFormLayout()
        form.addRow("Тип", self.type_combo)
        form.addRow("Параметры (YAML)", self.params_edit)
        form.addRow("Условия (YAML)", self.when_edit)
        form.addRow("Retry (YAML)", self.retry_edit)
        form.addRow("Fallback (YAML список)", self.on_failure_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_action(self) -> Optional[Dict[str, Any]]:
        if self.exec() != QDialog.Accepted:
            return None
        action = {
            "type": self.type_combo.currentText(),
            "params": _load_yaml(self.params_edit.toPlainText()),
            "when": _load_yaml(self.when_edit.toPlainText()),
            "retry": _load_yaml(self.retry_edit.toPlainText()),
            "on_failure": _load_yaml(self.on_failure_edit.toPlainText()) or [],
        }
        action = {k: v for k, v in action.items() if v}
        return action


class ProfileDialog(QDialog):
    def __init__(self, profile_id: str, apps: List[str], data: Dict[str, Any]) -> None:
        super().__init__()
        self.setWindowTitle("Профиль")
        self.profile_id = profile_id
        self._data = data

        self.allow_parallel = QCheckBox("Разрешить параллельный запуск")
        self.allow_parallel.setChecked(bool(data.get("allow_parallel", False)))

        self.app_list = QListWidget()
        for app_id in apps:
            item = QListWidgetItem(app_id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if app_id in data.get("apps", []) else Qt.Unchecked)
            self.app_list.addItem(item)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Профиль: {profile_id}"))
        layout.addWidget(self.allow_parallel)
        layout.addWidget(QLabel("Приложения"))
        layout.addWidget(self.app_list)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_profile(self) -> Optional[Dict[str, Any]]:
        if self.exec() != QDialog.Accepted:
            return None
        apps = []
        for idx in range(self.app_list.count()):
            item = self.app_list.item(idx)
            if item.checkState() == Qt.Checked:
                apps.append(item.text())
        return {
            "apps": apps,
            "allow_parallel": self.allow_parallel.isChecked(),
        }


def _dump_yaml(value: Any) -> str:
    if value is None or value == {} or value == []:
        return ""
    return yaml.safe_dump(value, sort_keys=False).strip()


def _load_yaml(text: str) -> Any:
    if not text.strip():
        return None
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError:
        return None
