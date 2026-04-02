# WinPos

WinPos — модульный фреймворк автоматизации для Windows 11. Система запускает, размещает и управляет любыми приложениями на нескольких мониторах через конфигурацию, а не через захардкоженные сценарии. Архитектура готова к будущему GUI-редактору.

## Возможности
- Реестр приложений и профилей.
- Переиспользуемые action-цепочки.
- WinAPI-управление окнами (pywin32).
- Динамическое определение мониторов и ролей.
- Последовательная очередь UI-действий как fallback.
- Безопасные повторы, тайм-ауты, базовая устойчивость.
- Готово к упаковке в `.exe` через PyInstaller.

## Быстрый старт
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python orchestrator\main.py
```

## Конфигурация
- Основной файл: `config/config.yaml`
- Схема: `config/schema.json`

Пример приложения:
```yaml
apps:
  notepad:
    display_name: "Notepad"
    launch:
      cmd: "notepad.exe"
    window_match:
      title_contains: "Notepad"
    actions:
      - type: launch_app
      - type: use_chain
        params:
          name: basic_window_setup
```

## Экшены
Поддерживаются универсальные типы:
- `launch_app`, `wait_for_process`, `wait_for_window`
- `bring_to_foreground`, `move_window_to_monitor`, `center_window`
- `resize_window`, `maximize`, `minimize`
- `send_hotkeys`, `send_text`, `open_url`
- `wait_for_title_change`, `wait_for_visibility`
- `use_chain` для переиспользуемых последовательностей

## Сборка в .exe (PyInstaller)
```powershell
pyinstaller --onefile --name WinPos orchestrator\main.py
```

## Структура проекта
```
actions/           # engine + примитивы действий
config/            # config.yaml + schema.json + менеджер
launcher/          # запуск процессов
monitors/          # обнаружение мониторов и роли
orchestrator/      # entrypoint и scheduler
registry/          # реестр приложений/профилей
recovery/          # watchdog (плейсхолдер)
state/             # состояние исполнения
ui/                # последовательная очередь UI действий
windows/           # WinAPI управление окнами
utils/             # ожидания/ретраи
logging_system/    # логирование
```
