
import pytest
from pydantic import ValidationError

from app.security import hash_password, verify_password
from app.schemas import UserCreate


def test_password_hashing():
    password = "SecureTest123!"
    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$argon2id$")


def test_correct_password():
    password = "SecureTest123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_incorrect_password():
    hashed = hash_password("SecureTest123!")

    assert verify_password("WrongPassword", hashed) is False


def test_valid_user_schema():
    user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="SecureTest123!"
    )

    assert user.username == "testuser"
    assert user.email == "test@example.com"


def test_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            username="testuser",
            email="invalid-email",
            password="SecureTest123!"
        )


def test_short_password():
    with pytest.raises(ValidationError):
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="123"
        )
