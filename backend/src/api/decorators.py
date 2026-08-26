from __future__ import annotations

from functools import wraps
from typing import Any, Callable
from uuid import UUID
from flask import g, request
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from src.api.errors import AppError, UnauthorizedError
from src.infrastructure.security.rate_limiter import RateLimiter
from src.infrastructure.security.token_service import TokenService

_token_service = TokenService()
_rate_limiter = RateLimiter()


def jwt_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator ensuring request has a valid, non-blacklisted Bearer JWT."""

    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise UnauthorizedError("Missing or invalid Authorization header")

        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = _token_service.decode_token(token)
        except ExpiredSignatureError:
            raise UnauthorizedError("Token has expired")
        except InvalidTokenError as e:
            raise UnauthorizedError(f"Invalid token: {str(e)}")

        if payload.get("type") != "access":
            raise UnauthorizedError("Access token required")

        g.current_user_id = UUID(payload["sub"])
        g.token_jti = payload.get("jti")
        g.token_exp = payload.get("exp")
        return f(*args, **kwargs)

    return decorated


def rate_limit(max_requests: int = 10, window_seconds: int = 60) -> Callable[..., Any]:
    """Decorator applying sliding window rate limiting by IP address."""

    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def decorated(*args: Any, **kwargs: Any) -> Any:
            ip = request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1")
            endpoint = request.endpoint or "unknown"
            key = f"{ip}:{endpoint}"

            if not _rate_limiter.is_allowed(key, max_requests, window_seconds):
                raise AppError(
                    "Too many requests. Please try again shortly.",
                    code="RATE_LIMIT_EXCEEDED",
                    status_code=429,
                )
            return f(*args, **kwargs)

        return decorated

    return decorator