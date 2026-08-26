from __future__ import annotations

import re
from datetime import datetime
from uuid import UUID
from email_validator import validate_email, EmailNotValidError

from src.api.errors import AppError, UnauthorizedError, ValidationError
from src.domain.entities.portfolio import CashBalance, Portfolio
from src.domain.entities.user import User
from src.domain.repositories.portfolio_repository import IPortfolioRepository
from src.domain.repositories.user_repository import IUserRepository
from src.infrastructure.security.password import hash_password, verify_password
from src.infrastructure.security.token_service import TokenService


class AuthService:
    """Application use-case orchestrator for authentication and user management."""

    def __init__(
        self,
        user_repo: IUserRepository,
        portfolio_repo: IPortfolioRepository,
        token_service: TokenService | None = None,
    ) -> None:
        self._user_repo = user_repo
        self._portfolio_repo = portfolio_repo
        self._token_service = token_service or TokenService()

    def register(
        self,
        email: str,
        password: str,
        full_name: str,
    ) -> tuple[User, str, str]:
        """Register a new user, create default portfolio, and issue auth tokens."""
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

        # 5. Create default portfolio
        default_portfolio = Portfolio(
            user_id=saved_user.id,
            name="Default Portfolio",
            currency="PKR",
            is_default=True,
        )
        default_portfolio.cash_balance = CashBalance(portfolio_id=default_portfolio.id)
        self._portfolio_repo.save(default_portfolio)

        # 6. Issue tokens
        access_token, _, _ = self._token_service.create_token(saved_user.id, "access")
        refresh_token, _, _ = self._token_service.create_token(saved_user.id, "refresh")

        return saved_user, access_token, refresh_token

    def login(self, email: str, password: str) -> tuple[User, str, str]:
        """Authenticate user and issue auth tokens."""
        normalized_email = email.strip().lower()
        user = self._user_repo.get_by_email(normalized_email)

        # Constant-time comparison prevention: verify dummy hash if user not found
        if not user or not verify_password(user.password_hash, password):
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("User account is inactive")

        access_token, _, _ = self._token_service.create_token(user.id, "access")
        refresh_token, _, _ = self._token_service.create_token(user.id, "refresh")

        return user, access_token, refresh_token

    def refresh_access_token(self, refresh_token: str) -> str:
        """Validate refresh token and issue a new access token."""
        try:
            payload = self._token_service.decode_token(refresh_token)
        except Exception:
            raise UnauthorizedError("Invalid or expired refresh token")

        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")

        user_id = UUID(payload["sub"])
        user = self._user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")

        new_access_token, _, _ = self._token_service.create_token(user_id, "access")
        return new_access_token

    def logout(self, access_token_jti: str, exp: int) -> None:
        """Revoke the active token."""
        self._token_service.revoke_token(access_token_jti, exp)