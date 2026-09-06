from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal
from uuid import UUID, uuid4
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from src.config import Settings, get_settings
from src.infrastructure.cache.memory_cache import get_cache


class TokenService:
    """Service for encoding, decoding, and revoking JWT access and refresh tokens."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._explicit_settings = settings
    
    @property
    def _settings(self) -> Settings:
        return self._explicit_settings or get_settings()

    def create_token(
        self,
        user_id: UUID,
        token_type: Literal["access", "refresh"] = "access",
        role: str = "user",
    ) -> tuple[str, str, datetime]:
        """Create a JWT token. Returns (encoded_token, jti, expiry_datetime)."""
        jti = str(uuid4())
        now = datetime.now(timezone.utc)

        if token_type == "access":
            expire_delta = timedelta(minutes=self._settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        else:
            expire_delta = timedelta(days=self._settings.REFRESH_TOKEN_EXPIRE_DAYS)

        exp = now + expire_delta
        payload: dict[str, Any] = {
            "sub": str(user_id),
            "role": role,
            "jti": jti,
            "type": token_type,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
        }

        token = jwt.encode(
            payload,
            self._settings.JWT_SECRET_KEY,
            algorithm=self._settings.JWT_ALGORITHM,
        )
        return token, jti, exp

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and validate a JWT token string. Raises InvalidTokenError on failure."""
        payload = jwt.decode(
            token,
            self._settings.JWT_SECRET_KEY,
            algorithms=[self._settings.JWT_ALGORITHM],
        )

        # Check token blacklist in Redis
        jti = payload.get("jti")
        if jti and self.is_token_blacklisted(jti):
            raise InvalidTokenError("Token has been revoked")

        # Check user-level revocation (e.g. password reset or account deletion)
        user_id = payload.get("sub")
        iat = payload.get("iat")
        if user_id and iat and self.is_user_revoked(user_id, iat):
            raise InvalidTokenError("User session has been revoked")

        return payload

    def revoke_token(self, jti: str, expires_at: datetime | int) -> None:
        """Add token jti to Redis blacklist until expiration."""
        client = get_cache()
        if client is None:
            return

        if isinstance(expires_at, datetime):
            ttl_seconds = max(1, int((expires_at - datetime.now(timezone.utc)).total_seconds()))
        else:
            ttl_seconds = max(1, int(expires_at - datetime.now(timezone.utc).timestamp()))

        try:
            client.setex(f"blacklist:token:{jti}", ttl_seconds, "revoked")
        except Exception:
            pass

    def is_token_blacklisted(self, jti: str) -> bool:
        """Check if a token jti is present in the Redis blacklist."""
        client = get_cache()
        if client is None:
            return False
        try:
            return bool(client.exists(f"blacklist:token:{jti}"))
        except Exception:
            return False

    def revoke_all_user_tokens(self, user_id: UUID | str) -> None:
        """Invalidate all active tokens for a user by recording the revocation timestamp."""
        client = get_cache()
        if client is None:
            return
        now_ts = int(datetime.now(timezone.utc).timestamp())
        ttl = max(self._settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400, 3600)
        try:
            client.setex(f"user:revoked_before:{str(user_id)}", ttl, str(now_ts))
        except Exception:
            pass

    def is_user_revoked(self, user_id: str, token_iat: int) -> bool:
        """Check if token was issued prior to user-level token invalidation."""
        client = get_cache()
        if client is None:
            return False
        try:
            val = client.get(f"user:revoked_before:{user_id}")
            if val is not None:
                revoked_before = int(val)
                return token_iat < revoked_before
        except Exception:
            pass
        return False

    def clear_user_cache(self, user_id: UUID | str) -> None:
        """Clean up user-specific cache keys without affecting other users."""
        client = get_cache()
        if client is None:
            return
        try:
            client.delete(f"user:revoked_before:{str(user_id)}")
        except Exception:
            pass