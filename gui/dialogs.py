"""GUI dialogs for WinPos."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pathlib import Path

import yaml
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
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
    QWidget,
)


ACTION_DEFS: Dict[str, Dict[str, Any]] = {
    "launch_app": {
        "label": "Запуск приложения",
        "desc": "Запускает приложение, если оно ещё не запущено.",
        "fields": [],
    },
    "wait_for_process": {
        "label": "Ожидание процесса",
        "desc": "Ожидает появления процесса приложения.",
        "fields": [
            {
                "name": "timeout_s",
                "label": "Таймаут (сек)",
                "type": "float",
                "help": "Сколько ждать процесс (например 10).",
            }
        ],
    },
    "wait_for_window": {
        "label": "Ожидание окна",
        "desc": "Ожидает появления окна по правилам window_match.",
        "fields": [
            {
                "name": "timeout_s",
                "label": "Таймаут (сек)",
                "type": "float",
                "help": "Сколько ждать окно (например 10).",
            }
        ],
    },
    "bring_to_foreground": {
        "label": "На передний план",
        "desc": "Выводит окно на передний план и активирует его.",
        "fields": [],
    },
    "move_window_to_monitor": {
        "label": "Переместить на монитор",
        "desc": "Перемещает окно на монитор с выбранной ролью.",
        "fields": [
            {
                "name": "monitor_role",
                "label": "Роль монитора",
                "type": "role",
                "help": "Например primary, secondary, third.",
            }
        ],
    },
    "center_window": {
        "label": "Центрировать окно",
        "desc": "Центрирует окно на выбранном мониторе.",
        "fields": [
            {
                "name": "monitor_role",
                "label": "Роль монитора",
                "type": "role",
                "help": "Например primary, secondary, third.",
            }
        ],
    },
    "resize_window": {
        "label": "Изменить размер",
        "desc": "Меняет размер окна на указанные значения.",
        "fields": [
            {
                "name": "width",
                "label": "Ширина (px)",
                "type": "int",
                "help": "Например 1280.",
            },
            {
                "name": "height",
                "label": "Высота (px)",
                "type": "int",
                "help": "Например 720.",
            },
        ],
    },
    "maximize": {
        "label": "Развернуть",
        "desc": "Разворачивает окно на весь экран.",
        "fields": [],
    },
    "minimize": {
        "label": "Свернуть",
        "desc": "Сворачивает окно в панель задач.",
        "fields": [],
    },
    "send_hotkeys": {
        "label": "Горячие клавиши",
        "desc": "Отправляет комбинацию клавиш в активное окно.",
        "fields": [
            {
                "name": "keys",
                "label": "Комбинация",
                "type": "str",
                "help": "Примеры: ctrl+shift+p, alt+f4.",
            }
        ],
    },
    "send_text": {
        "label": "Ввод текста",
        "desc": "Вводит текст в активное окно.",
        "fields": [
            {
                "name": "text",
                "label": "Текст",
                "type": "text",
                "help": "Текст будет введён в активное окно.",
            },
            {
                "name": "enter_after",
                "label": "Нажать Enter",
                "type": "bool",
                "help": "Если включено, нажимается Enter после ввода.",
            },
        ],
    },
    "open_url": {
        "label": "Открыть ссылку",
        "desc": "Открывает URL или deep‑link в браузере/приложении.",
        "fields": [
            {
                "name": "url",
                "label": "URL/ссылка",
                "type": "str",
                "help": "Пример: https://example.com или app://route.",
            }
        ],
    },
    "wait_for_title_change": {
        "label": "Ожидание заголовка",
        "desc": "Ждёт, когда в заголовке окна появится нужный текст.",
        "fields": [
            {
                "name": "contains",
                "label": "Текст в заголовке",
                "type": "str",
                "help": "Например: Документ или Сохранено.",
            },
            {
                "name": "timeout_s",
                "label": "Таймаут (сек)",
                "type": "float",
                "help": "Сколько ждать изменения заголовка.",
            },
        ],
    },
    "wait_for_visibility": {
        "label": "Ожидание видимости",
        "desc": "Ждёт, пока окно станет видимым.",
        "fields": [
            {
                "name": "timeout_s",
                "label": "Таймаут (сек)",
                "type": "float",
                "help": "Сколько ждать видимость окна.",
            }
        ],
    },
    "use_chain": {
        "label": "Использовать цепочку",
        "desc": "Запускает заранее описанную цепочку действий.",
        "fields": [
            {
                "name": "name",
                "label": "Имя цепочки",
                "type": "chain",
                "help": "Имя цепочки из action_chains.",
            }
        ],
    },
}

CONDITION_OPTIONS = [
    ("Без условия", None),
    ("Если процесс запущен", "process_running"),
    ("Если окно найдено", "window_exists"),
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

        self.app_id_edit.setPlaceholderText("например: notepad")
        self.app_id_edit.setToolTip("Уникальный ID. Без пробелов.")
        self.display_name_edit.setPlaceholderText("Например: Блокнот")
        self.display_name_edit.setToolTip("Название будет видно в списках.")

        self.cmd_edit.setPlaceholderText("C:\\Program Files\\App\\app.exe или notepad.exe")
        self.cmd_edit.setToolTip("Команда запуска. Можно указать exe или системную команду.")
        self.args_edit.setPlaceholderText("--profile default, /safe")
        self.args_edit.setToolTip("Аргументы запуска. Через запятую.")
        self.cwd_edit.setPlaceholderText("C:\\Program Files\\App")
        self.cwd_edit.setToolTip("Рабочая папка. Оставьте пустым, если не нужно.")

        self.title_contains_edit.setPlaceholderText("например: Notepad")
        self.title_contains_edit.setToolTip("Фрагмент заголовка окна.")
        self.title_equals_edit.setPlaceholderText("Полный заголовок")
        self.title_equals_edit.setToolTip("Точное совпадение заголовка.")
        self.class_name_edit.setPlaceholderText("например: Notepad")
        self.class_name_edit.setToolTip("Имя класса окна (WinAPI).")
        self.process_name_edit.setPlaceholderText("notepad.exe")
        self.process_name_edit.setToolTip("Имя процесса, если нужно точнее.")

        self.pick_cmd_btn = QPushButton("Выбрать exe")
        self.pick_cmd_btn.setToolTip("Выбрать исполняемый файл.")
        self.pick_cmd_btn.clicked.connect(self._pick_exe)
        self.pick_cwd_btn = QPushButton("Папка")
        self.pick_cwd_btn.setToolTip("Выбрать рабочую папку.")
        self.pick_cwd_btn.clicked.connect(self._pick_cwd)

        self.window_combo = QComboBox()
        self.refresh_windows_btn = QPushButton("Обновить окна")
        self.apply_window_btn = QPushButton("Заполнить из окна")
        self.refresh_windows_btn.clicked.connect(self._refresh_windows)
        self.apply_window_btn.clicked.connect(self._apply_window_selection)

        self.window_combo.setToolTip("Выберите окно из запущенных приложений.")
        self.apply_window_btn.setToolTip("Заполнит поля window_match по выбранному окну.")
        self.refresh_windows_btn.setToolTip("Обновить список видимых окон.")

        basic_form = QFormLayout()
        basic_form.addRow("ID", self.app_id_edit)
        basic_form.addRow("Название", self.display_name_edit)

        cmd_row = QHBoxLayout()
        cmd_row.addWidget(self.cmd_edit)
        cmd_row.addWidget(self.pick_cmd_btn)
        cmd_container = QWidget()
        cmd_container.setLayout(cmd_row)
        launch_form = QFormLayout()
        launch_form.addRow("Команда", cmd_container)
        launch_form.addRow("Аргументы (через ,)", self.args_edit)

        cwd_row = QHBoxLayout()
        cwd_row.addWidget(self.cwd_edit)
        cwd_row.addWidget(self.pick_cwd_btn)
        cwd_container = QWidget()
        cwd_container.setLayout(cwd_row)
        launch_form.addRow("Рабочая папка", cwd_container)

        window_form = QFormLayout()
        window_form.addRow("Заголовок содержит", self.title_contains_edit)
        window_form.addRow("Заголовок равен", self.title_equals_edit)
        window_form.addRow("Класс окна", self.class_name_edit)
        window_form.addRow("Имя процесса", self.process_name_edit)

        window_row = QHBoxLayout()
        window_row.addWidget(self.window_combo)
        window_row.addWidget(self.refresh_windows_btn)
        window_row.addWidget(self.apply_window_btn)
        window_container = QWidget()
        window_container.setLayout(window_row)
        window_form.addRow("Запущенные окна", window_container)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        basic_label = QLabel("Основное")
        basic_label.setObjectName("SectionTitle")
        launch_label = QLabel("Запуск")
        launch_label.setObjectName("SectionTitle")
        window_label = QLabel("Поиск окна")
        window_label.setObjectName("SectionTitle")

        layout.addWidget(basic_label)
        layout.addLayout(basic_form)
        layout.addSpacing(8)
        layout.addWidget(launch_label)
        layout.addLayout(launch_form)
        layout.addSpacing(8)
        layout.addWidget(window_label)
        layout.addLayout(window_form)
        layout.addWidget(buttons)
        self.setLayout(layout)

        if app_id:
            self.app_id_edit.setDisabled(True)
        self._refresh_windows()

    def _pick_exe(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Выберите exe", "", "Executable (*.exe);;All Files (*)")
        if path:
            self.cmd_edit.setText(path)
            if not self.display_name_edit.text().strip():
                self.display_name_edit.setText(Path(path).stem)

    def _pick_cwd(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if path:
            self.cwd_edit.setText(path)

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
    def __init__(
        self,
        action: Optional[Dict[str, Any]] = None,
        monitor_roles: Optional[List[Dict[str, str]]] = None,
        chain_names: Optional[List[str]] = None,
        allow_fallback: bool = True,
    ) -> None:
        super().__init__()
        self.setWindowTitle("Действие")
        self._action = action or {}
        self._monitor_roles = monitor_roles or []
        self._chain_names = chain_names or []
        self._allow_fallback = allow_fallback
        self._field_widgets: Dict[str, QWidget] = {}

        self.type_combo = QComboBox()
        for action_id, info in ACTION_DEFS.items():
            self.type_combo.addItem(info["label"], action_id)
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        self.type_combo.setToolTip("Выберите тип действия.")

        self.description = QLabel("")
        self.description.setWordWrap(True)

        self.params_container = QWidget()
        self.params_form = QFormLayout()
        self.params_container.setLayout(self.params_form)

        self.condition_combo = QComboBox()
        for label, value in CONDITION_OPTIONS:
            self.condition_combo.addItem(label, value)
        self.condition_combo.setToolTip("Условие выполнения действия.")

        self.retry_enabled = QCheckBox("Повторы при ошибке")
        self.retry_enabled.setToolTip("Если действие не удалось, повторить его.")
        self.retry_count = QLineEdit()
        self.retry_count.setPlaceholderText("2")
        self.retry_count.setValidator(QIntValidator(0, 10))
        self.retry_count.setToolTip("Сколько повторов выполнить.")
        self.retry_delay = QLineEdit()
        self.retry_delay.setPlaceholderText("0.5")
        self.retry_delay.setValidator(QDoubleValidator(0.0, 60.0, 2))
        self.retry_delay.setToolTip("Пауза между повторами (сек).")

        self.fallback_list = QListWidget()
        self.add_fallback_btn = QPushButton("Добавить fallback")
        self.edit_fallback_btn = QPushButton("Изменить")
        self.remove_fallback_btn = QPushButton("Удалить")
        self.add_fallback_btn.setToolTip("Действия, которые выполняются при ошибке.")
        self.edit_fallback_btn.setToolTip("Редактировать выбранный fallback.")
        self.remove_fallback_btn.setToolTip("Удалить выбранный fallback.")

        self.add_fallback_btn.clicked.connect(self.add_fallback)
        self.edit_fallback_btn.clicked.connect(self.edit_fallback)
        self.remove_fallback_btn.clicked.connect(self.remove_fallback)

        form = QFormLayout()
        form.addRow("Тип", self.type_combo)
        form.addRow("Описание", self.description)
        form.addRow("Параметры", self.params_container)
        form.addRow("Условие", self.condition_combo)

        retry_row = QHBoxLayout()
        retry_row.addWidget(self.retry_enabled)
        retry_row.addWidget(QLabel("Повторы"))
        retry_row.addWidget(self.retry_count)
        retry_row.addWidget(QLabel("Пауза (сек)"))
        retry_row.addWidget(self.retry_delay)
        form.addRow("Повторы", retry_row)

        if self._allow_fallback:
            fallback_row = QHBoxLayout()
            fallback_row.addWidget(self.add_fallback_btn)
            fallback_row.addWidget(self.edit_fallback_btn)
            fallback_row.addWidget(self.remove_fallback_btn)
            fallback_box = QVBoxLayout()
            fallback_box.addWidget(self.fallback_list)
            fallback_box.addLayout(fallback_row)
            fallback_container = QWidget()
            fallback_container.setLayout(fallback_box)
            form.addRow("Fallback", fallback_container)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

        self._load_action(self._action)

    def _load_action(self, action: Dict[str, Any]) -> None:
        action_type = action.get("type", "launch_app")
        index = self._find_type_index(action_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        self._build_fields(action_type, action.get("params", {}))
        when = action.get("when") or {}
        when_type = when.get("type")
        for idx in range(self.condition_combo.count()):
            if self.condition_combo.itemData(idx) == when_type:
                self.condition_combo.setCurrentIndex(idx)
                break
        retry = action.get("retry") or {}
        if retry:
            self.retry_enabled.setChecked(True)
            self.retry_count.setText(str(retry.get("retries", "")))
            self.retry_delay.setText(str(retry.get("delay_s", "")))
        if self._allow_fallback:
            for item in action.get("on_failure", []) or []:
                self._add_fallback_item(item)

    def _find_type_index(self, action_type: str) -> int:
        for idx in range(self.type_combo.count()):
            if self.type_combo.itemData(idx) == action_type:
                return idx
        return -1

    def _on_type_changed(self) -> None:
        action_type = self.type_combo.currentData()
        info = ACTION_DEFS.get(action_type, {})
        self.description.setText(info.get("desc", ""))
        self._build_fields(action_type, {})

    def _clear_layout(self, layout: QFormLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _build_fields(self, action_type: str, params: Dict[str, Any]) -> None:
        self._field_widgets.clear()
        self._clear_layout(self.params_form)
        info = ACTION_DEFS.get(action_type, {})
        self.description.setText(info.get("desc", ""))

        for field in info.get("fields", []):
            widget: QWidget
            ftype = field.get("type")
            label_text = field.get("label", field.get("name"))
            help_text = field.get("help", "")
            label = QLabel(label_text)
            if help_text:
                label.setToolTip(help_text)

            if ftype == "text":
                widget = QPlainTextEdit()
                widget.setToolTip(help_text)
                if params.get(field["name"]):
                    widget.setPlainText(str(params.get(field["name"])))
            elif ftype == "bool":
                widget = QCheckBox("Включено")
                widget.setToolTip(help_text)
                widget.setChecked(bool(params.get(field["name"], False)))
            elif ftype == "int":
                widget = QLineEdit(str(params.get(field["name"], "")))
                widget.setValidator(QIntValidator(0, 100000))
                widget.setToolTip(help_text)
            elif ftype == "float":
                widget = QLineEdit(str(params.get(field["name"], "")))
                widget.setValidator(QDoubleValidator(0.0, 100000.0, 2))
                widget.setToolTip(help_text)
            elif ftype == "role":
                combo = QComboBox()
                combo.setEditable(False)
                for role in self._monitor_roles:
                    combo.addItem(role["label"], role["value"])
                current = str(params.get(field["name"], ""))
                if current:
                    for idx in range(combo.count()):
                        if combo.itemData(idx) == current:
                            combo.setCurrentIndex(idx)
                            break
                combo.setToolTip(help_text)
                widget = combo
            elif ftype == "chain":
                combo = QComboBox()
                combo.setEditable(True)
                for chain in self._chain_names:
                    combo.addItem(chain)
                current = str(params.get(field["name"], ""))
                if current:
                    combo.setCurrentText(current)
                combo.setToolTip(help_text)
                widget = combo
            else:
                widget = QLineEdit(str(params.get(field["name"], "")))
                widget.setToolTip(help_text)
            self.params_form.addRow(label, widget)
            self._field_widgets[field["name"]] = widget

    def _collect_params(self) -> Optional[Dict[str, Any]]:
        action_type = self.type_combo.currentData()
        info = ACTION_DEFS.get(action_type, {})
        params: Dict[str, Any] = {}
        for field in info.get("fields", []):
            name = field["name"]
            ftype = field.get("type")
            widget = self._field_widgets.get(name)
            if widget is None:
                continue
            if ftype == "text":
                value = widget.toPlainText().strip()  # type: ignore[union-attr]
            elif ftype == "bool":
                value = bool(widget.isChecked())  # type: ignore[union-attr]
                if not value:
                    continue
            elif ftype in ("int", "float"):
                raw = widget.text().strip()  # type: ignore[union-attr]
                if not raw:
                    continue
                try:
                    value = int(raw) if ftype == "int" else float(raw)
                except ValueError:
                    QMessageBox.warning(self, "Ошибка", f"Некорректное значение: {name}")
                    return None
            else:
                if isinstance(widget, QComboBox):
                    data = widget.currentData()
                    value = str(data) if data is not None else widget.currentText().strip()
                else:
                    value = widget.text().strip()  # type: ignore[union-attr]
                if not value:
                    continue
            params[name] = value
        return params

    def _add_fallback_item(self, action: Dict[str, Any]) -> None:
        label = _format_action(action)
        item = QListWidgetItem(label)
        item.setData(Qt.UserRole, action)
        self.fallback_list.addItem(item)

    def add_fallback(self) -> None:
        dialog = ActionDialog(monitor_roles=self._monitor_roles, chain_names=self._chain_names, allow_fallback=False)
        action = dialog.get_action()
        if action:
            self._add_fallback_item(action)

    def edit_fallback(self) -> None:
        row = self.fallback_list.currentRow()
        if row < 0:
            return
        item = self.fallback_list.item(row)
        action = item.data(Qt.UserRole)
        dialog = ActionDialog(action=action, monitor_roles=self._monitor_roles, chain_names=self._chain_names, allow_fallback=False)
        updated = dialog.get_action()
        if updated:
            item.setText(_format_action(updated))
            item.setData(Qt.UserRole, updated)

    def remove_fallback(self) -> None:
        row = self.fallback_list.currentRow()
        if row < 0:
            return
        self.fallback_list.takeItem(row)

    def get_action(self) -> Optional[Dict[str, Any]]:
        if self.exec() != QDialog.Accepted:
            return None
        action_type = self.type_combo.currentData()
        params = self._collect_params()
        if params is None:
            return None

        action: Dict[str, Any] = {"type": action_type}
        if params:
            action["params"] = params

        condition = self.condition_combo.currentData()
        if condition:
            action["when"] = {"type": condition}

        if self.retry_enabled.isChecked():
            retries = int(self.retry_count.text() or "1")
            delay = float(self.retry_delay.text() or "0.5")
            action["retry"] = {"retries": retries, "delay_s": delay}

        if self._allow_fallback:
            fallbacks = []
            for idx in range(self.fallback_list.count()):
                item = self.fallback_list.item(idx)
                fallbacks.append(item.data(Qt.UserRole))
            if fallbacks:
                action["on_failure"] = fallbacks
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


def _format_action(action: Dict[str, Any]) -> str:
    params = action.get("params") or {}
    summary = ""
    if params:
        summary = ", ".join(f"{k}={v}" for k, v in params.items())
    action_type = action.get("type", "")
    label = ACTION_DEFS.get(action_type, {}).get("label", action_type)
    return f"{label} {summary}".strip()


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
