"""Live GUI smoke test. Opt-in only.

Run it where a window can open, for example under Xvfb on Linux::

    SS_KIVYMD_GUI_TESTS=1 xvfb-run -a pytest tests/test_ui_smoke.py

or on Windows with the environment variable set. It is skipped by
default (including in CI) because it needs Kivy, KivyMD, and a display.
The app is pointed at a temporary database with ``SS_KIVYMD_DB_PATH``.
"""

import os

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("SS_KIVYMD_GUI_TESTS") != "1",
    reason="GUI smoke test needs SS_KIVYMD_GUI_TESTS=1 and a display",
)

kivymd = pytest.importorskip("kivymd")
pytest.importorskip("kivy")

from kivy.clock import Clock  # noqa: E402

from user_management.app import UserManagementApp  # noqa: E402


def test_add_and_delete_through_the_interface(tmp_path, monkeypatch):
    monkeypatch.setenv("KIVY_NO_ARGS", "1")
    monkeypatch.setenv("SS_KIVYMD_DB_PATH", str(tmp_path / "users.db"))
    app = UserManagementApp()
    state: dict[str, bool] = {}

    def interact(_dt):
        interface = app.root
        assert interface is not None
        interface.username_field.text = "ada"
        interface.email_field.text = "ada@example.com"
        interface.add_user()
        assert interface.db.get_users()[0].username == "ada"
        assert len(interface.user_list.children) == 1

        interface._select_user(interface.db.get_users()[0].user_id)
        interface.delete_selected()
        assert interface.db.get_users() == []
        assert len(interface.user_list.children) == 0
        assert interface.status_label.text.startswith("Deleted")
        state["done"] = True
        app.stop()

    Clock.schedule_once(interact, 0.2)
    Clock.schedule_once(lambda _dt: app.stop(), 5)
    app.run()
    assert state.get("done") is True
    assert kivymd.__version__.startswith("2.")
