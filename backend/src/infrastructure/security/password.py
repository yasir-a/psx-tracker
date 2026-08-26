from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# OWASP recommended Argon2id parameters
_ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,  # 64 MB
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using Argon2id."""
    return _ph.hash(plain_password)


def verify_password(hashed_password: str, plain_password: str) -> bool:
    """Verify plaintext password against an Argon2id hash."""
    try:
        return _ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, Exception):
        return False