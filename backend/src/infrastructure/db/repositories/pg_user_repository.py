from __future__ import annotations

from uuid import UUID
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from src.domain.entities.user import User
from src.domain.repositories.user_repository import IUserRepository
from src.infrastructure.db.models.user_model import UserModel


class PgUserRepository(IUserRepository):
    """PostgreSQL implementation of IUserRepository using SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            role=getattr(model, "role", "user") or "user",
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, user: User) -> User:
        model = self._session.get(UserModel, user.id)
        if model is None:
            model = UserModel(
                id=user.id,
                email=user.email,
                password_hash=user.password_hash,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            self._session.add(model)
        else:
            model.email = user.email
            model.password_hash = user.password_hash
            model.full_name = user.full_name
            model.role = user.role
            model.is_active = user.is_active
            model.updated_at = user.updated_at
        self._session.flush()
        return self._to_entity(model)

    def get_by_id(self, user_id: UUID) -> User | None:
        model = self._session.get(UserModel, user_id)
        return self._to_entity(model) if model else None

    def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email.lower().strip())
        model = self._session.execute(stmt).scalar_one_or_none()
        return self._to_entity(model) if model else None

    def list_all(
        self, limit: int = 50, offset: int = 0, search: str | None = None
    ) -> tuple[list[User], int]:
        stmt = select(UserModel)
        count_stmt = select(func.count(UserModel.id))

        if search:
            term = f"%{search.strip().lower()}%"
            filter_clause = or_(
                UserModel.email.ilike(term),
                UserModel.full_name.ilike(term),
            )
            stmt = stmt.where(filter_clause)
            count_stmt = count_stmt.where(filter_clause)

        total = self._session.execute(count_stmt).scalar() or 0
        stmt = stmt.order_by(UserModel.created_at.desc()).limit(limit).offset(offset)
        models = self._session.scalars(stmt).all()

        return [self._to_entity(m) for m in models], total

    def count_admins(self) -> int:
        stmt = select(func.count(UserModel.id)).where(
            UserModel.role == "admin",
            UserModel.is_active.is_(True),
        )
        return self._session.execute(stmt).scalar() or 0

    def delete(self, user_id: UUID) -> bool:
        model = self._session.get(UserModel, user_id)
        if model:
            self._session.delete(model)
            self._session.flush()
            return True
        return False