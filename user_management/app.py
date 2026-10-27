"""Application entry point."""

from __future__ import annotations

from kivymd.app import MDApp

from user_management.user_interface import UserInterface


class UserManagementApp(MDApp):
    def build(self) -> UserInterface:
        self.title = "User Management System"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        self._interface = UserInterface()
        return self._interface

    def on_stop(self) -> None:
        interface = getattr(self, "_interface", None)
        if interface is not None:
            interface.close()


def main() -> None:
    UserManagementApp().run()
