# User Management System

A small desktop user manager in Python, built with Kivy and KivyMD 2.0. Add a username and email, see everyone in a scrollable Material Design 3 list, tap a row to select them, and delete them. Nothing leaves your machine: users live in a local SQLite database.

This is a demo, not an accounts system. There is no login, no password, and no sync. Usernames and emails are unique, case-insensitively, and the email check only verifies the shape `name@example.com`.

## Run it

Python 3.10 or higher.

```bash
git clone https://github.com/enonymous1/kivymd-user-manager.git
cd kivymd-user-manager
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install .
user-management
```

Or, without installing, from the project root:

```bash
pip install -r requirements.txt
python main.py
```

`requirements.txt` pins the same versions as `pyproject.toml` (`kivy==2.3.1`, `kivymd==2.0.0`) for a plain `pip install -r` workflow.

The database is created in the app's user-data directory (for example `%APPDATA%\User Management System` on Windows) as `users.db`. It is git-ignored and never committed. Set `SS_KIVYMD_DB_PATH` to point it elsewhere; the GUI smoke test uses that override.

## What changed in 2.0.0

The original demo used 1.x widget names, an `MDTooltip` pretending to be a toolbar, and a drawer added as a plain layout child, with unpinned dependencies and no validation. Version 2.0.0 rebuilds the interface on KivyMD 2.0's composition APIs:

- `MDTopAppBar` with a menu button (toggles the drawer), a title, and a refresh button, built from leading/trailing button containers.
- `MDTextField` in outlined mode, with hint and helper text as child widgets, plus the field error state on invalid input.
- `MDButton` with `MDButtonText` children for Add User and Delete selected.
- `MDListItem` rows (headline username, supporting email) inside a scroll view.
- `MDNavigationDrawer` inside `MDNavigationLayout`, with a drawer menu. Home closes the drawer; Settings shows a status note, since there is no settings screen in this demo.

See [CHANGELOG.md](CHANGELOG.md) for the full list.

## Project structure

```text
kivymd-user-manager/
├── main.py                    # `python main.py` entry point
├── pyproject.toml             # packaging, pinned deps, lint/type config
├── requirements.txt           # pinned deps for a plain pip install
└── user_management/
    ├── __init__.py            # package version only (no Kivy import)
    ├── app.py                 # MDApp subclass and console-script entry
    ├── user_db.py             # SQLite storage (unique, context manager)
    ├── user_interface.py      # KivyMD 2.0 interface
    └── user_model.py          # User dataclass and validation
```

## Development

```bash
pip install ".[dev]"
ruff check . && ruff format --check .
mypy user_management
python -m pytest tests -q
```

The headless tests cover the model and database. The GUI smoke test needs a display and is opt-in, so CI does not run it:

```bash
# Linux example:
SS_KIVYMD_GUI_TESTS=1 xvfb-run -a python -m pytest tests/test_ui_smoke.py -q
```

Verification status: 22 headless tests, ruff, format, and mypy pass, and the GUI smoke test (build the real interface, add a user, select and delete it) passes under Xvfb on Linux with Kivy 2.3.1 / KivyMD 2.0.0. The on-screen look — colours, spacing, drawer animation — still needs an eyeball on Windows after push: a framebuffer export on this box came out black, so no screenshot is claimed. The widget composition was also checked against the kivymd 2.0.0 package source.

## License

MIT — see [LICENSE](LICENSE).
