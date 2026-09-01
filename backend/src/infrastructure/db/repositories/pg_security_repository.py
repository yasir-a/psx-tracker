from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session

from src.domain.market.quote import DataStatus, HistoricalPrice, MarketQuote
from src.domain.market.security import Security, SecurityType
from src.domain.repositories.security_repository import ISecurityRepository
from src.domain.values.money import Money
from src.infrastructure.db.models.security_model import HistoricalPriceModel, SecurityModel


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
        model = self._session.scalars(stmt).first()
        return self._to_entity(model) if model else None

    def list_all(self, active_only: bool = True) -> list[Security]:
        stmt = select(SecurityModel)
        if active_only:
            stmt = stmt.where(SecurityModel.is_active.is_(True))
        stmt = stmt.order_by(SecurityModel.symbol.asc())
        models = self._session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    def search(self, query: str) -> list[Security]:
        term = f"%{query.strip()}%"
        stmt = (
            select(SecurityModel)
            .where(
                or_(
                    SecurityModel.symbol.ilike(term),
                    SecurityModel.name.ilike(term),
                )
            )
            .order_by(SecurityModel.symbol.asc())
        )
        models = self._session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    # --- Market Price Persistence (Source of Truth Fallback) ---

    def save_historical_price(self, price: HistoricalPrice) -> None:
        stmt = select(HistoricalPriceModel).where(
            HistoricalPriceModel.symbol == price.symbol,
            HistoricalPriceModel.trade_date == price.trade_date,
        )
        model = self._session.scalars(stmt).first()
        if model is None:
            model = HistoricalPriceModel(
                symbol=price.symbol,
                trade_date=price.trade_date,
                open_price=price.open_price.amount,
                high_price=price.high_price.amount,
                low_price=price.low_price.amount,
                close_price=price.close_price.amount,
                volume=price.volume,
            )
            self._session.add(model)
        else:
            model.open_price = price.open_price.amount
            model.high_price = price.high_price.amount
            model.low_price = price.low_price.amount
            model.close_price = price.close_price.amount
            model.volume = price.volume
        self._session.flush()

    def get_latest_persisted_quote(self, symbol: str) -> MarketQuote | None:
        """Fetch the most recent persisted market price from PostgreSQL as fallback."""
        stmt = (
            select(HistoricalPriceModel)
            .where(HistoricalPriceModel.symbol == symbol.upper().strip())
            .order_by(desc(HistoricalPriceModel.trade_date))
            .limit(2)
        )
        models = self._session.scalars(stmt).all()
        if not models:
            return None

        latest = models[0]
        prev = models[1] if len(models) > 1 else latest

        return MarketQuote.create(
            symbol=latest.symbol,
            current_price=Money(latest.close_price, "PKR"),
            previous_close=Money(prev.close_price, "PKR"),
            volume=latest.volume,
            updated_at=datetime.combine(latest.trade_date, datetime.min.time(), tzinfo=timezone.utc),
            status=DataStatus.STALE,
        )

    def get_historical_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalPrice]:
        stmt = (
            select(HistoricalPriceModel)
            .where(
                HistoricalPriceModel.symbol == symbol.upper().strip(),
                HistoricalPriceModel.trade_date >= start_date,
                HistoricalPriceModel.trade_date <= end_date,
            )
            .order_by(HistoricalPriceModel.trade_date.asc())
        )
        models = self._session.scalars(stmt).all()
        return [
            HistoricalPrice(
                symbol=m.symbol,
                trade_date=m.trade_date,
                open_price=Money(m.open_price, "PKR"),
                high_price=Money(m.high_price, "PKR"),
                low_price=Money(m.low_price, "PKR"),
                close_price=Money(m.close_price, "PKR"),
                volume=m.volume,
            )
            for m in models
        ]