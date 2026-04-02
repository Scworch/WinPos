"""Main GUI window."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QInputDialog,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QSystemTrayIcon,
    QMenu,
)

from gui.config_store import ConfigStore
from gui.dialogs import AppDialog, ActionDialog, ProfileDialog


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("WinPos")
        self.resize(1100, 720)

        self.config_path = Path(__file__).resolve().parents[1] / "config" / "config.yaml"
        self.store = ConfigStore(self.config_path)
        self.data: Dict[str, Any] = self.store.load()

        self._setup_ui()
        self._setup_tray()
        self._refresh_profiles()
        self._refresh_apps()

    def _setup_ui(self) -> None:
        toolbar = QToolBar("Main")
        toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(toolbar)

        save_action = QAction("Сохранить", self)
        save_action.triggered.connect(self.save_config)
        toolbar.addAction(save_action)

        validate_action = QAction("Проверить", self)
        validate_action.triggered.connect(self.validate_config)
        toolbar.addAction(validate_action)

        splitter = QSplitter(Qt.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        self.profile_combo = QComboBox()
        self.profile_combo.currentTextChanged.connect(self._on_profile_changed)
        left_layout.addWidget(QLabel("Профиль"))
        left_layout.addWidget(self.profile_combo)

        profile_buttons = QHBoxLayout()
        add_profile_btn = QPushButton("Добавить профиль")
        add_profile_btn.clicked.connect(self.add_profile)
        edit_profile_btn = QPushButton("Редактировать")
        edit_profile_btn.clicked.connect(self.edit_profile)
        profile_buttons.addWidget(add_profile_btn)
        profile_buttons.addWidget(edit_profile_btn)
        left_layout.addLayout(profile_buttons)

        left_layout.addWidget(QLabel("Приложения"))
        self.app_list = QListWidget()
        self.app_list.currentItemChanged.connect(self._on_app_selected)
        left_layout.addWidget(self.app_list)

        app_buttons = QHBoxLayout()
        add_app_btn = QPushButton("Добавить")
        add_app_btn.clicked.connect(self.add_app)
        edit_app_btn = QPushButton("Изменить")
        edit_app_btn.clicked.connect(self.edit_app)
        remove_app_btn = QPushButton("Удалить")
        remove_app_btn.clicked.connect(self.remove_app)
        app_buttons.addWidget(add_app_btn)
        app_buttons.addWidget(edit_app_btn)
        app_buttons.addWidget(remove_app_btn)
        left_layout.addLayout(app_buttons)

        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        self.detail_form = QFormLayout()
        self.detail_display_name = QLabel("—")
        self.detail_cmd = QLabel("—")
        self.detail_match = QLabel("—")
        self.detail_form.addRow("Название", self.detail_display_name)
        self.detail_form.addRow("Команда", self.detail_cmd)
        self.detail_form.addRow("Окно", self.detail_match)
        right_layout.addLayout(self.detail_form)

        right_layout.addWidget(QLabel("Действия"))
        self.action_list = QListWidget()
        right_layout.addWidget(self.action_list)

        action_buttons = QHBoxLayout()
        add_action_btn = QPushButton("Добавить действие")
        add_action_btn.clicked.connect(self.add_action)
        edit_action_btn = QPushButton("Изменить")
        edit_action_btn.clicked.connect(self.edit_action)
        remove_action_btn = QPushButton("Удалить")
        remove_action_btn.clicked.connect(self.remove_action)
        move_up_btn = QPushButton("Вверх")
        move_up_btn.clicked.connect(lambda: self.move_action(-1))
        move_down_btn = QPushButton("Вниз")
        move_down_btn.clicked.connect(lambda: self.move_action(1))
        action_buttons.addWidget(add_action_btn)
        action_buttons.addWidget(edit_action_btn)
        action_buttons.addWidget(remove_action_btn)
        action_buttons.addWidget(move_up_btn)
        action_buttons.addWidget(move_down_btn)
        right_layout.addLayout(action_buttons)

        right_layout.addWidget(QLabel("Preview"))
        self.preview_box = QPlainTextEdit()
        self.preview_box.setReadOnly(True)
        right_layout.addWidget(self.preview_box)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        container = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(splitter)
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _setup_tray(self) -> None:
        icon_path = Path(__file__).resolve().parents[1] / "assets" / "icon.svg"
        icon = QIcon(str(icon_path)) if icon_path.exists() else self.windowIcon()
        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip("WinPos")

        menu = QMenu()
        show_action = QAction("Открыть/скрыть", self)
        show_action.triggered.connect(self.toggle_visibility)
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        menu.addAction(show_action)
        menu.addAction(exit_action)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if hasattr(self, "tray") and self.tray.isVisible():
            event.ignore()
            self.hide()
            return
        super().closeEvent(event)

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.Trigger:
            self.toggle_visibility()

    def toggle_visibility(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def _refresh_profiles(self) -> None:
        profiles = list((self.data.get("profiles") or {}).keys())
        if not profiles:
            profiles = ["default"]
            self.data.setdefault("profiles", {})["default"] = {"apps": []}
        self.profile_combo.clear()
        self.profile_combo.addItems(profiles)
        default_profile = self.data.get("settings", {}).get("default_profile", profiles[0])
        if default_profile in profiles:
            self.profile_combo.setCurrentText(default_profile)

    def _refresh_apps(self) -> None:
        self.app_list.clear()
        apps = self.data.get("apps", {})
        for app_id in sorted(apps.keys()):
            item = QListWidgetItem(app_id)
            self.app_list.addItem(item)
        if self.app_list.count() > 0:
            self.app_list.setCurrentRow(0)

    def _on_profile_changed(self, profile_id: str) -> None:
        settings = self.data.setdefault("settings", {})
        settings["default_profile"] = profile_id
        self._refresh_apps()

    def _on_app_selected(self) -> None:
        item = self.app_list.currentItem()
        if not item:
            return
        app_id = item.text()
        app = (self.data.get("apps") or {}).get(app_id, {})
        self.detail_display_name.setText(app.get("display_name", ""))
        self.detail_cmd.setText((app.get("launch") or {}).get("cmd", ""))
        match = app.get("window_match", {})
        match_text = ", ".join(f"{k}={v}" for k, v in match.items()) if match else "—"
        self.detail_match.setText(match_text)
        self._refresh_actions(app)
        self._update_preview(app)

    def _refresh_actions(self, app: Dict[str, Any]) -> None:
        self.action_list.clear()
        for action in app.get("actions", []) or []:
            label = self._format_action(action)
            self.action_list.addItem(label)

    def _format_action(self, action: Dict[str, Any]) -> str:
        params = action.get("params") or {}
        summary = ""
        if params:
            summary = ", ".join(f"{k}={v}" for k, v in params.items())
        return f"{action.get('type', '')} {summary}".strip()

    def _update_preview(self, app: Dict[str, Any]) -> None:
        actions = app.get("actions", []) or []
        lines: List[str] = []
        for action in actions:
            if action.get("type") == "use_chain":
                name = (action.get("params") or {}).get("name")
                lines.append(f"use_chain: {name}")
                chain = (self.data.get("action_chains") or {}).get(name, [])
                for chain_action in chain:
                    lines.append(f"  - {self._format_action(chain_action)}")
            else:
                lines.append(f"- {self._format_action(action)}")
        self.preview_box.setPlainText("\n".join(lines) if lines else "Нет действий")

    def add_app(self) -> None:
        dialog = AppDialog()
        result = dialog.get_data()
        if not result:
            return
        app_id = result["app_id"]
        self.data.setdefault("apps", {})[app_id] = result["data"]
        self._refresh_apps()

    def edit_app(self) -> None:
        item = self.app_list.currentItem()
        if not item:
            return
        app_id = item.text()
        app = (self.data.get("apps") or {}).get(app_id, {})
        dialog = AppDialog(app_id=app_id, data=app)
        result = dialog.get_data()
        if not result:
            return
        self.data.setdefault("apps", {})[app_id] = result["data"]
        self._refresh_apps()

    def remove_app(self) -> None:
        item = self.app_list.currentItem()
        if not item:
            return
        app_id = item.text()
        apps = self.data.get("apps", {})
        if app_id in apps:
            del apps[app_id]
        for profile in (self.data.get("profiles") or {}).values():
            if app_id in profile.get("apps", []):
                profile["apps"] = [a for a in profile.get("apps", []) if a != app_id]
        self._refresh_apps()

    def _current_app(self) -> Dict[str, Any]:
        item = self.app_list.currentItem()
        if not item:
            return {}
        app_id = item.text()
        return (self.data.get("apps") or {}).get(app_id, {})

    def add_action(self) -> None:
        app = self._current_app()
        if not app:
            return
        dialog = ActionDialog()
        action = dialog.get_action()
        if not action:
            return
        app.setdefault("actions", []).append(action)
        self._refresh_actions(app)
        self._update_preview(app)

    def edit_action(self) -> None:
        app = self._current_app()
        if not app:
            return
        row = self.action_list.currentRow()
        if row < 0:
            return
        actions = app.get("actions", [])
        dialog = ActionDialog(action=actions[row])
        action = dialog.get_action()
        if not action:
            return
        actions[row] = action
        self._refresh_actions(app)
        self._update_preview(app)

    def remove_action(self) -> None:
        app = self._current_app()
        if not app:
            return
        row = self.action_list.currentRow()
        if row < 0:
            return
        actions = app.get("actions", [])
        actions.pop(row)
        self._refresh_actions(app)
        self._update_preview(app)

    def move_action(self, direction: int) -> None:
        app = self._current_app()
        if not app:
            return
        row = self.action_list.currentRow()
        if row < 0:
            return
        actions = app.get("actions", [])
        new_index = row + direction
        if new_index < 0 or new_index >= len(actions):
            return
        actions[row], actions[new_index] = actions[new_index], actions[row]
        self._refresh_actions(app)
        self.action_list.setCurrentRow(new_index)
        self._update_preview(app)

    def add_profile(self) -> None:
        name, ok = _prompt_text(self, "Новый профиль", "ID профиля")
        if not ok or not name:
            return
        profiles = self.data.setdefault("profiles", {})
        profiles[name] = {"apps": []}
        self._refresh_profiles()

    def edit_profile(self) -> None:
        profile_id = self.profile_combo.currentText()
        if not profile_id:
            return
        profiles = self.data.setdefault("profiles", {})
        profile = profiles.get(profile_id, {"apps": []})
        apps = sorted((self.data.get("apps") or {}).keys())
        dialog = ProfileDialog(profile_id, apps, profile)
        result = dialog.get_profile()
        if not result:
            return
        profiles[profile_id] = result
        self._refresh_profiles()

    def save_config(self) -> None:
        issues = self.store.validate(self.data)
        if issues:
            QMessageBox.warning(self, "Ошибка", "; ".join(issues))
            return
        self.store.save(self.data)
        QMessageBox.information(self, "Сохранено", "Конфигурация сохранена")

    def validate_config(self) -> None:
        issues = self.store.validate(self.data)
        if issues:
            QMessageBox.warning(self, "Проверка", "; ".join(issues))
        else:
            QMessageBox.information(self, "Проверка", "Ошибок не найдено")


def _prompt_text(parent: QWidget, title: str, label: str) -> tuple[str, bool]:
    text, ok = QInputDialog.getText(parent, title, label)
    return text.strip(), bool(ok)
