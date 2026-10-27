"""KivyMD 2.0 user interface.

Built imperatively with ``add_widget`` on purpose: every 2.0 widget used
here routes its children in its own ``add_widget`` (app-bar containers and
title, text-field hint/helper text, button text, list-item parts, drawer
menu items), so the composition below matches the widgets' own contracts
in kivymd 2.0.0 rather than relying on a declarative-constructor shape.

Layout: an ``MDNavigationLayout`` holding a screen manager (app bar, form,
scrollable list) and a modal navigation drawer. Tap a list row to select
that user, then use Delete selected to remove them.
"""

from __future__ import annotations

import os
from pathlib import Path

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.appbar import (
    MDActionTopAppBarButton,
    MDTopAppBar,
    MDTopAppBarLeadingButtonContainer,
    MDTopAppBarTitle,
    MDTopAppBarTrailingButtonContainer,
)
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (
    MDList,
    MDListItem,
    MDListItemHeadlineText,
    MDListItemLeadingIcon,
    MDListItemSupportingText,
)
from kivymd.uix.navigationdrawer import (
    MDNavigationDrawer,
    MDNavigationDrawerDivider,
    MDNavigationDrawerItem,
    MDNavigationDrawerItemLeadingIcon,
    MDNavigationDrawerItemText,
    MDNavigationDrawerLabel,
    MDNavigationDrawerMenu,
    MDNavigationLayout,
)
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldHelperText,
    MDTextFieldHintText,
)

from user_management.user_db import UserDB
from user_management.user_model import User, validate_email, validate_username


class UserInterface(MDNavigationLayout):
    """Root widget: navigation layout with one screen and a drawer."""

    def __init__(self, db_path: str | Path | None = None, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(**kwargs)
        self._db_path = (
            Path(db_path) if db_path is not None else self._default_db_path()
        )
        self.db = UserDB(self._db_path)
        self._selected_user_id: int | None = None
        self._rows: dict[int, MDListItem] = {}
        self._build_layout()
        self.load_users()

    # -- construction -------------------------------------------------

    def _default_db_path(self) -> Path:
        """Per-app data dir when an app is running, else the work dir.

        ``SS_KIVYMD_DB_PATH`` overrides the location. It exists for the
        GUI smoke test; the shipped app never sets it.
        """
        override = os.environ.get("SS_KIVYMD_DB_PATH")
        if override:
            return Path(override)
        try:
            from kivy.app import App

            app = App.get_running_app()
            if app is not None:
                return Path(app.user_data_dir) / "users.db"
        except Exception:  # pragma: no cover - defensive fallback
            pass
        return Path.cwd() / "users.db"

    def _build_layout(self) -> None:
        screen_manager = MDScreenManager()
        screen = MDScreen(name="main")
        content = MDBoxLayout(orientation="vertical")
        content.add_widget(self._build_app_bar())
        content.add_widget(self._build_form())
        content.add_widget(self._build_list_view())
        screen.add_widget(content)
        screen_manager.add_widget(screen)
        self.add_widget(screen_manager)

        self.nav_drawer = MDNavigationDrawer()
        self.nav_drawer.add_widget(self._build_drawer_menu())
        self.add_widget(self.nav_drawer)

    def _build_app_bar(self) -> MDTopAppBar:
        bar = MDTopAppBar(type="small")

        leading = MDTopAppBarLeadingButtonContainer()
        leading.add_widget(
            MDActionTopAppBarButton(
                icon="menu",
                on_release=lambda *args: self.nav_drawer.set_state("toggle"),
            )
        )
        bar.add_widget(leading)

        bar.add_widget(MDTopAppBarTitle(text="User Management System"))

        trailing = MDTopAppBarTrailingButtonContainer()
        trailing.add_widget(
            MDActionTopAppBarButton(
                icon="refresh",
                on_release=lambda *args: self._refresh(),
            )
        )
        bar.add_widget(trailing)
        return bar

    def _build_form(self) -> MDBoxLayout:
        form = MDBoxLayout(
            orientation="vertical",
            padding=(dp(16), dp(16), dp(16), dp(8)),
            spacing=dp(12),
            adaptive_height=True,
        )

        self.username_field = MDTextField(mode="outlined")
        self.username_field.add_widget(MDTextFieldHintText(text="Username"))
        self.username_field.add_widget(
            MDTextFieldHelperText(text="Required. Must be unique.", mode="persistent")
        )
        self.username_field.bind(text=self._on_field_text)
        form.add_widget(self.username_field)

        self.email_field = MDTextField(mode="outlined")
        self.email_field.add_widget(MDTextFieldHintText(text="Email"))
        self.email_field.add_widget(
            MDTextFieldHelperText(
                text="Required. Must look like name@example.com.",
                mode="persistent",
            )
        )
        self.email_field.bind(text=self._on_field_text)
        form.add_widget(self.email_field)

        buttons = BoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            size_hint_y=None,
            height=dp(48),
        )
        add_button = MDButton(style="filled", on_release=self.add_user)
        add_button.add_widget(MDButtonText(text="Add User"))
        buttons.add_widget(add_button)

        self.delete_button = MDButton(
            style="outlined", on_release=self.delete_selected, disabled=True
        )
        self.delete_button.add_widget(MDButtonText(text="Delete selected"))
        buttons.add_widget(self.delete_button)
        form.add_widget(buttons)

        self.status_label = MDLabel(text="", size_hint_y=None, height=dp(20))
        form.add_widget(self.status_label)
        return form

    def _build_list_view(self) -> ScrollView:
        scroll = ScrollView()
        self.user_list = MDList()
        scroll.add_widget(self.user_list)
        return scroll

    def _build_drawer_menu(self) -> MDNavigationDrawerMenu:
        menu = MDNavigationDrawerMenu()
        menu.add_widget(MDNavigationDrawerLabel(text="User Management"))
        menu.add_widget(MDNavigationDrawerDivider())
        menu.add_widget(self._drawer_item("home", "Home", self._drawer_home))
        menu.add_widget(self._drawer_item("cog", "Settings", self._drawer_settings))
        return menu

    def _drawer_item(self, icon: str, text: str, handler) -> MDNavigationDrawerItem:  # type: ignore[no-untyped-def]
        item = MDNavigationDrawerItem()
        item.add_widget(MDNavigationDrawerItemLeadingIcon(icon=icon))
        item.add_widget(MDNavigationDrawerItemText(text=text))
        item.bind(on_release=lambda *args: handler())
        return item

    # -- behaviour ----------------------------------------------------

    def _on_field_text(self, field: MDTextField, _value: str) -> None:
        field.error = False

    def _refresh(self) -> None:
        self._selected_user_id = None
        self._update_delete_button()
        self.load_users()
        self.status_label.text = "List refreshed."

    def _drawer_home(self) -> None:
        self.nav_drawer.set_state("close")

    def _drawer_settings(self) -> None:
        self.nav_drawer.set_state("close")
        self.status_label.text = "Settings is not implemented in this demo."

    def _update_delete_button(self) -> None:
        self.delete_button.disabled = self._selected_user_id is None

    def add_user(self, _instance: object = None) -> None:
        """Validate the form, store the user, and refresh the list."""
        username_text = self.username_field.text
        email_text = self.email_field.text
        username_error = False
        email_error = False
        try:
            username = validate_username(username_text)
        except ValueError as exc:
            username_error = True
            message = str(exc)
        try:
            email = validate_email(email_text)
        except ValueError as exc:
            email_error = True
            message = str(exc)
        self.username_field.error = username_error
        self.email_field.error = email_error
        if username_error or email_error:
            self.status_label.text = message
            return
        try:
            stored = self.db.add_user(User(None, username, email))
        except ValueError as exc:
            self.status_label.text = str(exc)
            return
        self.username_field.text = ""
        self.email_field.text = ""
        self._selected_user_id = None
        self._update_delete_button()
        self.load_users()
        self.status_label.text = f"Added {stored.username}."

    def delete_selected(self, _instance: object = None) -> None:
        """Delete the user selected by tapping a list row."""
        if self._selected_user_id is None:
            self.status_label.text = "Select a user first."
            return
        user_id = self._selected_user_id
        name = next(
            (user.username for user in self.db.get_users() if user.user_id == user_id),
            "user",
        )
        if self.db.delete_user(user_id):
            self.status_label.text = f"Deleted {name}."
        else:
            self.status_label.text = "That user was already gone."
        self._selected_user_id = None
        self._update_delete_button()
        self.load_users()

    def _select_user(self, user_id: int) -> None:
        self._selected_user_id = user_id
        self._update_delete_button()
        user = next(
            (
                row_user
                for row_user in self.db.get_users()
                if row_user.user_id == user_id
            ),
            None,
        )
        if user is not None:
            self.status_label.text = (
                f"Selected {user.username} ({user.email}). "
                "Tap Delete selected to remove them."
            )

    def load_users(self) -> None:
        self.user_list.clear_widgets()
        self._rows = {}
        for user in self.db.get_users():
            if user.user_id is None:  # pragma: no cover - defensive
                continue
            row = MDListItem()
            row.add_widget(MDListItemLeadingIcon(icon="account-circle"))
            row.add_widget(MDListItemHeadlineText(text=user.username))
            row.add_widget(MDListItemSupportingText(text=user.email))
            row.bind(on_release=lambda _row, uid=user.user_id: self._select_user(uid))
            self._rows[user.user_id] = row
            self.user_list.add_widget(row)

    def close(self) -> None:
        """Close the database connection. Called by the app on exit."""
        self.db.close()
