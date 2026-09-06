from __future__ import annotations

import logging
import re
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session

from src.api.errors import AppError, BadRequestError, NotFoundError, ValidationError
from src.domain.entities.user import User
from src.infrastructure.db.repositories.pg_portfolio_repository import PgPortfolioRepository
from src.infrastructure.db.repositories.pg_user_repository import PgUserRepository
from src.infrastructure.security.password import hash_password
from src.infrastructure.security.token_service import TokenService

logger = logging.getLogger(__name__)


class AdminService:
    """Service handling administrator management operations with audit logging."""

    def __init__(self, session: Session, token_service: TokenService | None = None) -> None:
        self._session = session
        self._user_repo = PgUserRepository(session)
        self._portfolio_repo = PgPortfolioRepository(session)
        self._token_service = token_service or TokenService()

    def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
    ) -> dict[str, Any]:
        """List registered users with pagination and search."""
        offset = max(0, (page - 1) * per_page)
        users, total = self._user_repo.list_all(limit=per_page, offset=offset, search=search)

        user_items = []
        for u in users:
            portfolios = self._portfolio_repo.get_by_user_id(u.id)
            user_items.append({
                "id": str(u.id),
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
                "is_active": u.is_active,
                "portfolio_count": len(portfolios),
                "created_at": u.created_at.isoformat(),
            })

        return {
            "users": user_items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": max(1, (total + per_page - 1) // per_page),
            },
        }

    def get_user_details(self, user_id: UUID) -> dict[str, Any]:
        """Retrieve user details and summary stats."""
        user = self._user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        portfolios = self._portfolio_repo.get_by_user_id(user.id)
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "portfolio_count": len(portfolios),
            "portfolios": [{"id": str(p.id), "name": p.name, "is_default": p.is_default} for p in portfolios],
            "created_at": user.created_at.isoformat(),
        }

    def reset_password(self, admin_id: UUID, target_user_id: UUID, new_password: str) -> None:
        """Reset user password and invalidate existing user sessions."""
        if len(new_password) < 8 or not re.search(r"[A-Za-z]", new_password) or not re.search(r"[0-9]", new_password):
            raise ValidationError("Password must be at least 8 characters long and contain both letters and numbers")

        user = self._user_repo.get_by_id(target_user_id)
        if not user:
            raise NotFoundError("User not found")

        # Update password hash
        user.password_hash = hash_password(new_password)
        self._user_repo.save(user)
        self._session.commit()

        # Invalidate all existing tokens/sessions in Redis
        self._token_service.revoke_all_user_tokens(target_user_id)
        logger.info("AUDIT: Admin %s reset password for User %s (%s)", str(admin_id), str(user.id), user.email)

    def delete_user(self, admin_id: UUID, target_user_id: UUID) -> None:
        """Permanently hard-delete a user and all associated database and cache records."""
        # Safeguard 1: Admin cannot delete their own account
        if admin_id == target_user_id:
            raise BadRequestError("Cannot delete your own administrator account")

        user = self._user_repo.get_by_id(target_user_id)
        if not user:
            raise NotFoundError("User not found")

        # Safeguard 2: Cannot delete the last administrator
        if user.role == "admin":
            admin_count = self._user_repo.count_admins()
            if admin_count <= 1:
                raise BadRequestError("Cannot delete the last remaining administrator account")

        target_email = user.email

        # Atomic deletion within transaction
        try:
            self._user_repo.delete(target_user_id)
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            logger.error("Failed to delete user %s: %s", str(target_user_id), str(e))
            raise AppError("Failed to delete user due to a database error", code="DELETE_FAILED", status_code=500)

        # Cleanup user cache and revoke tokens
        self._token_service.revoke_all_user_tokens(target_user_id)
        self._token_service.clear_user_cache(target_user_id)

        logger.info("AUDIT: Admin %s permanently deleted User %s (%s) and all associated records", str(admin_id), str(target_user_id), target_email)