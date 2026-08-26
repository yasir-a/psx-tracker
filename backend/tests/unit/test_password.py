from __future__ import annotations

from src.infrastructure.security.password import hash_password, verify_password


def test_password_hashing_and_verification() -> None:
    raw_password = "SecurePassword123!"
    hashed = hash_password(raw_password)

    assert hashed != raw_password
    assert hashed.startswith("$argon2id$")
    assert verify_password(hashed, raw_password) is True
    assert verify_password(hashed, "WrongPassword") is False