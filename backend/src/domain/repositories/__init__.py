"""Repository interfaces package."""

from src.domain.repositories.user_repository import IUserRepository
from src.domain.repositories.portfolio_repository import IPortfolioRepository

__all__ = ["IUserRepository", "IPortfolioRepository"]