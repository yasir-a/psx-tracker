from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.infrastructure.db.models.portfolio_model import PortfolioModel


class UserModel(Base, TimestampMixin):
    """SQLAlchemy model mapping to the 'users' table."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    portfolios: Mapped[list[PortfolioModel]] = relationship(
        "PortfolioModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )