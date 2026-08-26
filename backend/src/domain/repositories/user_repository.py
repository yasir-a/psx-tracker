from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.user import User


class IUserRepository(ABC):
    """Abstract interface for user data operations."""

    @abstractmethod
    def save(self, user: User) -> User:
        """Persist a new or modified user entity."""
        pass

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:
        """Retrieve user by UUID."""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        """Retrieve user by normalized email address."""
        pass

    @abstractmethod
    def delete(self, user_id: UUID) -> bool:
        """Delete user by ID. Returns True if deleted."""
        pass