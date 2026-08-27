from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.domain.market.security import Security, SecurityType
from src.domain.repositories.security_repository import ISecurityRepository
from src.infrastructure.db.models.security_model import SecurityModel


class PgSecurityRepository(ISecurityRepository):
    """PostgreSQL implementation of ISecurityRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def _to_entity(self, model: SecurityModel) -> Security:
        return Security(
            id=model.id,
            symbol=model.symbol,
            name=model.name,
            sector=model.sector,
            security_type=SecurityType(model.security_type),
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def save(self, security: Security) -> Security:
        model = self._session.get(SecurityModel, security.id)
        if model is None:
            model = SecurityModel(
                id=security.id,
                symbol=security.symbol,
                name=security.name,
                sector=security.sector,
                security_type=security.security_type,
                is_active=security.is_active,
                created_at=security.created_at,
                updated_at=security.updated_at,
            )
            self._session.add(model)
        else:
            model.name = security.name
            model.sector = security.sector
            model.security_type = security.security_type
            model.is_active = security.is_active
            model.updated_at = security.updated_at
        self._session.flush()
        return self._to_entity(model)

    def save_bulk(self, securities: list[Security]) -> int:
        count = 0
        for s in securities:
            self.save(s)
            count += 1
        return count

    def get_by_symbol(self, symbol: str) -> Security | None:
        stmt = select(SecurityModel).where(SecurityModel.symbol == symbol.upper().strip())
        model = self._session.execute(stmt).scalar_one_or_none()
        return self._to_entity(model) if model else None

    def search(self, query: str | None = None, sector: str | None = None, limit: int = 50) -> list[Security]:
        stmt = select(SecurityModel).where(SecurityModel.is_active.is_(True))

        if sector:
            stmt = stmt.where(SecurityModel.sector == sector)

        if query:
            clean_q = f"%{query.strip()}%"
            stmt = stmt.where(
                or_(
                    SecurityModel.symbol.ilike(clean_q),
                    SecurityModel.name.ilike(clean_q),
                )
            )

        stmt = stmt.order_by(SecurityModel.symbol.asc()).limit(limit)
        models = self._session.execute(stmt).scalars().all()
        return [self._to_entity(m) for m in models]