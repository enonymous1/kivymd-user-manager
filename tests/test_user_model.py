import pytest

from user_management.user_model import User, validate_email, validate_username


def test_user_strips_whitespace():
    user = User(None, "  ada  ", "  ada@example.com ")
    assert user.username == "ada"
    assert user.email == "ada@example.com"
    assert user.user_id is None


def test_username_must_not_be_empty():
    with pytest.raises(ValueError, match="Username"):
        validate_username("   ")


def test_username_too_long():
    with pytest.raises(ValueError, match="at most 64"):
        validate_username("a" * 65)


@pytest.mark.parametrize(
    "email",
    ["plainaddress", "ada@", "@example.com", "ada@example", "ada@exa mple.com", ""],
)
def test_invalid_emails_rejected(email):
    with pytest.raises(ValueError, match="Email"):
        validate_email(email)


@pytest.mark.parametrize(
    "email",
    ["ada@example.com", "ada.lovelace+demo@mail.example.co.uk"],
)
def test_valid_emails_accepted(email):
    assert validate_email(email) == email


def test_user_rejects_bad_email():
    with pytest.raises(ValueError, match="Email"):
        User(None, "ada", "not-an-email")


def test_user_id_must_be_positive_int_or_none():
    with pytest.raises(ValueError, match="user_id"):
        User(0, "ada", "ada@example.com")
    with pytest.raises(ValueError, match="user_id"):
        User("1", "ada", "ada@example.com")
    assert User(1, "ada", "ada@example.com").user_id == 1
