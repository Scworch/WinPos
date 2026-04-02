# WinPos

WinPos — приложение для автоматизации Windows 11: запуск, размещение и управление окнами приложений на нескольких мониторах через настраиваемые профили. Есть GUI‑редактор конфигурации.

## Возможности
- Запуск приложений и проверка, что они уже запущены
- Управление окнами через WinAPI (перемещение, центрирование, размер, maximize/minimize)
- Действия по цепочкам, условия, повторы, fallback
- Выбор физического монитора в GUI
- Логи в файл и консоль
- Упаковка в `.exe` через PyInstaller

## Требования
- Windows 11
- Python 3.11

## Установка
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Запуск
### Автоматизация (CLI)
```powershell
python orchestrator\main.py
```

### GUI‑редактор
```powershell
python gui\main.py
```

## Конфигурация
Файлы:
- `config/config.yaml` — личная конфигурация (не хранится в репозитории)
- `config/config.example.yaml` — пример
- `config/schema.json`

При первом запуске `config/config.yaml` создаётся автоматически на основе `DEFAULT_CONFIG`.

### Пример приложения
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

### Пример цепочки действий
```yaml
action_chains:
  basic_window_setup:
    - type: wait_for_window
      params:
        timeout_s: 10
    - type: bring_to_foreground
    - type: move_window_to_monitor
      params:
        monitor_role: primary
    - type: maximize
```

### Профили
```yaml
profiles:
  default:
    apps:
      - notepad
```

## Действия (основные)
- `launch_app`
- `wait_for_process`
- `wait_for_window`
- `bring_to_foreground`
- `move_window_to_monitor`
- `center_window`
- `resize_window`
- `maximize`, `minimize`
- `send_hotkeys`, `send_text`
- `open_url`
- `wait_for_title_change`, `wait_for_visibility`
- `use_chain`

## Логи
`logs/winpos.log`

## Сборка в .exe
```powershell
pyinstaller --onefile --name WinPos orchestrator\main.py
```

GUI можно собрать отдельно:
```powershell
pyinstaller --onefile --name WinPos-GUI gui\main.py
```

## Структура
```
actions/           # действия и engine
config/            # конфигурация
launcher/          # запуск процессов
logging_system/    # логирование
monitors/          # мониторы
orchestrator/      # выполнение профилей
registry/          # приложения/профили
state/             # состояние
ui/                # очередь UI‑действий
windows/           # WinAPI управление окнами
gui/               # GUI‑редактор
```

## Лицензия
См. `LICENSE`.
