from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from email_validator import EmailNotValidError, validate_email
from sqlalchemy.orm import Session

from src.api.errors import AppError, UnauthorizedError, ValidationError
from src.config import get_settings
from src.domain.entities.user import User
from src.infrastructure.cache.redis_client import get_redis_client
from src.infrastructure.db.repositories.pg_portfolio_repository import PgPortfolioRepository
from src.infrastructure.db.repositories.pg_user_repository import PgUserRepository
from src.infrastructure.security.password import hash_password, verify_password
from src.infrastructure.security.token_service import TokenService


class AuthService:
    """Application use-case coordinator for user registration, authentication, and token issuance."""

    def __init__(self, session: Session, token_service: TokenService | None = None) -> None:
        self._session = session
        self._user_repo = PgUserRepository(session)
        self._portfolio_repo = PgPortfolioRepository(session)
        self._token_service = token_service or TokenService()
        self._settings = get_settings()

    def register(
        self,
        email: str,
        password: str,
        full_name: str,
    ) -> tuple[User, str, str]:
        """Register a new user and issue auth tokens."""
        # 1. Validate & normalize email
        try:
            email_info = validate_email(email.strip(), check_deliverability=False)
            normalized_email = email_info.normalized.lower()
        except EmailNotValidError as e:
            raise ValidationError(f"Invalid email address: {str(e)}")

        # 2. Validate password strength
        if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            raise ValidationError("Password must be at least 8 characters long and contain both letters and numbers")

        if len(full_name.strip()) < 2:
            raise ValidationError("Full name must be at least 2 characters long")

        # 3. Check email uniqueness
        existing_user = self._user_repo.get_by_email(normalized_email)
        if existing_user:
            raise AppError("An account with this email already exists", code="EMAIL_ALREADY_EXISTS", status_code=409)

        # 4. Hash password & save user
        pwd_hash = hash_password(password)
        user = User(
            email=normalized_email,
            password_hash=pwd_hash,
            full_name=full_name.strip(),
        )
        saved_user = self._user_repo.save(user)

        # 5. Issue tokens
        access_token, _, _ = self._token_service.create_token(saved_user.id, "access")
        refresh_token, _, _ = self._token_service.create_token(saved_user.id, "refresh")

        return saved_user, access_token, refresh_token

    def login(self, email: str, password: str) -> tuple[User, str, str]:
        """Authenticate user and issue auth tokens."""
        normalized_email = email.strip().lower()
        user = self._user_repo.get_by_email(normalized_email)

        if not user or not user.is_active:
            raise UnauthorizedError("Invalid email or password")

        if not verify_password(user.password_hash, password):
            raise UnauthorizedError("Invalid email or password")

        access_token, _, _ = self._token_service.create_token(user.id, "access")
        refresh_token, _, _ = self._token_service.create_token(user.id, "refresh")

        return user, access_token, refresh_token

    def refresh(self, refresh_token_str: str) -> tuple[str, str]:
        """Exchange a valid refresh token for a fresh access/refresh token pair."""
        payload = self._token_service.decode_token(refresh_token_str)
        user_id = UUID(payload["sub"])

        user = self._user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("User inactive or no longer exists")

        new_access_token, _, _ = self._token_service.create_token(user.id, "access")
        new_refresh_token, _, _ = self._token_service.create_token(user.id, "refresh")

        return new_access_token, new_refresh_token

    def refresh_access_token(self, refresh_token_str: str) -> str:
        """Exchange a valid refresh token for a fresh access token."""
        access_token, _ = self.refresh(refresh_token_str)
        return access_token

    def logout(self, token_jti: str, token_exp: int) -> None:
        """Revoke the current access token in Redis blacklist until expiration."""
        client = get_redis_client(self._settings)
        if client is not None:
            now_ts = int(datetime.now(timezone.utc).timestamp())
            ttl = max(token_exp - now_ts, 1)
            try:
                client.setex(f"token:blacklist:{token_jti}", ttl, "1")
            except Exception:
                pass

    def get_user_profile(self, user_id: UUID) -> dict[str, Any]:
        """Retrieve user profile metadata."""
        user = self._user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")

        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "created_at": user.created_at.isoformat(),
        }