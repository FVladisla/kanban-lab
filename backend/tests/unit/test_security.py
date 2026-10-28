import pytest
from datetime import datetime, timezone, timedelta
from jose import jwt

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings


def test_hash_password_returns_string():
    h = hash_password("secret123")
    assert isinstance(h, str)
    assert h != "secret123"
    assert h.startswith("$2b$")


def test_hash_password_different_for_same_input():
    h1 = hash_password("secret123")
    h2 = hash_password("secret123")
    assert h1 != h2


def test_verify_password_correct():
    h = hash_password("secret123")
    assert verify_password("secret123", h) is True


def test_verify_password_incorrect():
    h = hash_password("secret123")
    assert verify_password("wrong", h) is False


def test_create_access_token_contains_fields():
    token = create_access_token(subject=42, role="admin")
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "42"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_create_refresh_token_contains_fields():
    token = create_refresh_token(subject=42)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "42"
    assert payload["type"] == "refresh"
    assert "exp" in payload


def test_decode_token_valid():
    token = create_access_token(subject=1, role="developer")
    data = decode_token(token)
    assert data["sub"] == "1"
    assert data["role"] == "developer"


def test_decode_token_invalid_raises():
    with pytest.raises(ValueError):
        decode_token("not-a-token")


def test_decode_token_wrong_signature_raises():
    token = jwt.encode({"sub": "1"}, "wrong-secret", algorithm="HS256")
    with pytest.raises(ValueError):
        decode_token(token)