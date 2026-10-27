import sqlite3

import pytest

from user_management.user_db import UserDB
from user_management.user_model import User


def _user(username="ada", email="ada@example.com"):
    return User(None, username, email)


def test_add_and_list_roundtrip(tmp_path):
    db = UserDB(tmp_path / "users.db")
    stored = db.add_user(_user())
    assert stored.user_id == 1
    assert db.get_users() == [stored]
    db.close()


def test_users_listed_in_id_order(tmp_path):
    db = UserDB(tmp_path / "users.db")
    first = db.add_user(_user("ada", "ada@example.com"))
    second = db.add_user(_user("grace", "grace@example.com"))
    assert db.get_users() == [first, second]
    db.close()


def test_duplicate_username_rejected_case_insensitively(tmp_path):
    db = UserDB(tmp_path / "users.db")
    db.add_user(_user("Ada", "ada@example.com"))
    with pytest.raises(ValueError, match="already exists"):
        db.add_user(_user("ada", "other@example.com"))
    db.close()


def test_duplicate_email_rejected_case_insensitively(tmp_path):
    db = UserDB(tmp_path / "users.db")
    db.add_user(_user("ada", "Ada@Example.com"))
    with pytest.raises(ValueError, match="already exists"):
        db.add_user(_user("grace", "ada@example.com"))
    db.close()


def test_delete_user(tmp_path):
    db = UserDB(tmp_path / "users.db")
    stored = db.add_user(_user())
    assert db.delete_user(stored.user_id) is True
    assert db.delete_user(stored.user_id) is False
    assert db.get_users() == []
    db.close()


def test_data_persists_across_reopen(tmp_path):
    path = tmp_path / "users.db"
    db = UserDB(path)
    stored = db.add_user(_user())
    db.close()
    reopened = UserDB(path)
    assert reopened.get_users() == [stored]
    reopened.close()


def test_in_memory_database(tmp_path):
    db = UserDB(":memory:")
    assert db.add_user(_user()).user_id == 1
    assert len(db.get_users()) == 1
    db.close()


def test_context_manager_closes(tmp_path):
    with UserDB(tmp_path / "users.db") as db:
        db.add_user(_user())
        assert not db.closed
    assert db.closed
    db.close()  # idempotent
    assert db.closed


def test_database_file_created_in_nested_directory(tmp_path):
    path = tmp_path / "nested" / "data" / "users.db"
    db = UserDB(path)
    db.add_user(_user())
    db.close()
    assert path.exists()
    assert sqlite3.connect(path).execute("SELECT COUNT(*) FROM users").fetchone() == (
        1,
    )
