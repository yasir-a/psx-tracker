from __future__ import annotations

from uuid import uuid4
import pytest
from jwt.exceptions import InvalidTokenError

from src.infrastructure.security.token_service import TokenService


def test_token_creation_and_decoding() -> None:
    service = TokenService()
    user_id = uuid4()

    token, jti, exp = service.create_token(user_id, "access")
    assert token is not None
    assert jti is not None

    payload = service.decode_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["jti"] == jti
    assert payload["type"] == "access"


def test_invalid_token_decoding() -> None:
    service = TokenService()
    with pytest.raises(InvalidTokenError):
        service.decode_token("invalid.token.payload")