"""SQLite storage for users.

Usernames and emails are unique, case-insensitively, so the same person
cannot be added twice under a different capitalisation. Duplicate adds
raise ``ValueError`` instead of leaking ``sqlite3.IntegrityError`` to
the interface layer.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from user_management.user_model import User

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE
)
"""


class UserDB:
    """A small SQLite-backed user store. Use as a context manager."""

    def __init__(self, db_path: str | Path = "users.db") -> None:
        self._db_path = Path(db_path)
        parent = self._db_path.parent
        if str(parent) not in ("", "."):
            parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self._db_path)
        self._closed = False
        self.create_table()

    @property
    def db_path(self) -> Path:
        return self._db_path

    @property
    def closed(self) -> bool:
        return self._closed

    def create_table(self) -> None:
        with self._conn:
            self._conn.execute(_SCHEMA)

    def add_user(self, user: User) -> User:
        """Store ``user`` and return it with its new ``user_id`` set."""
        try:
            with self._conn:
                cursor = self._conn.execute(
                    "INSERT INTO users (username, email) VALUES (?, ?)",
                    (user.username, user.email),
                )
        except sqlite3.IntegrityError as exc:
            raise ValueError(
                "A user with that username or email already exists."
            ) from exc
        stored_id = cursor.lastrowid
        if stored_id is None:  # pragma: no cover - defensive
            raise RuntimeError("Insert did not return a row id.")
        return User(stored_id, user.username, user.email)

    def get_users(self) -> list[User]:
        cursor = self._conn.execute(
            "SELECT user_id, username, email FROM users ORDER BY user_id"
        )
        return [User(row[0], row[1], row[2]) for row in cursor]

    def delete_user(self, user_id: int) -> bool:
        """Delete one user. Returns ``True`` when a row was removed."""
        with self._conn:
            cursor = self._conn.execute(
                "DELETE FROM users WHERE user_id = ?", (user_id,)
            )
        return cursor.rowcount > 0

    def close(self) -> None:
        """Close the connection. Safe to call more than once."""
        if not self._closed:
            self._closed = True
            self._conn.close()

    def __enter__(self) -> UserDB:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
