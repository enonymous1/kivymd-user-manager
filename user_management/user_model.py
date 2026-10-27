"""User data model with validation.

The validation here is a format check only: a username must be present
and an email must look like ``name@example.com``. It says nothing about
whether the address exists or can receive mail.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

MAX_USERNAME_LENGTH = 64


def validate_username(username: str) -> str:
    """Return the stripped username, or raise ``ValueError``."""
    cleaned = username.strip()
    if not cleaned:
        raise ValueError("Username must not be empty.")
    if len(cleaned) > MAX_USERNAME_LENGTH:
        raise ValueError(f"Username must be at most {MAX_USERNAME_LENGTH} characters.")
    return cleaned


def validate_email(email: str) -> str:
    """Return the stripped email, or raise ``ValueError``."""
    cleaned = email.strip()
    if not cleaned:
        raise ValueError("Email must not be empty.")
    if not _EMAIL_RE.match(cleaned):
        raise ValueError("Email must look like name@example.com.")
    return cleaned


@dataclass
class User:
    """A single user. ``user_id`` is ``None`` until the row is stored."""

    user_id: int | None
    username: str
    email: str

    def __post_init__(self) -> None:
        if self.user_id is not None:
            if not isinstance(self.user_id, int) or isinstance(self.user_id, bool):
                raise ValueError("user_id must be an int or None.")
            if self.user_id < 1:
                raise ValueError("user_id must be a positive int or None.")
        self.username = validate_username(self.username)
        self.email = validate_email(self.email)
