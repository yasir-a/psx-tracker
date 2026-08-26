from __future__ import annotations

from typing import Generator
from flask import Flask, g
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from src.config import Settings, get_settings

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None
_scoped_session: scoped_session[Session] | None = None


def get_engine(settings: Settings | None = None) -> Engine:
    """Create or return the cached SQLAlchemy engine."""
    global _engine
    if _engine is None:
        cfg = settings or get_settings()
        engine_kwargs: dict[str, Any] = {
            "echo": False,
        }
        # SQLite in-memory doesn't support QueuePool args (pool_size, max_overflow)
        if not cfg.DATABASE_URL.startswith("sqlite"):
            engine_kwargs.update({
                "pool_pre_ping": True,
                "pool_size": 10,
                "max_overflow": 20,
            })
        _engine = create_engine(cfg.DATABASE_URL, **engine_kwargs)
    return _engine


def get_session_factory(settings: Settings | None = None) -> sessionmaker[Session]:
    """Create or return the cached sessionmaker."""
    global _session_factory, _scoped_session
    if _session_factory is None:
        engine = get_engine(settings)
        _session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
        _scoped_session = scoped_session(_session_factory)
    return _session_factory


def get_db_session() -> Session:
    """Retrieve the active request-scoped database session."""
    if "db_session" not in g:
        factory = get_session_factory()
        g.db_session = factory()
    return g.db_session


def close_db_session(exception: BaseException | None = None) -> None:
    """Close and tear down the current request database session."""
    session: Session | None = g.pop("db_session", None)
    if session is not None:
        if exception:
            session.rollback()
        session.close()


def init_db(app: Flask, settings: Settings | None = None) -> None:
    """Initialize database engine and register Flask session lifecycle teardown."""
    get_engine(settings)
    get_session_factory(settings)
    app.teardown_appcontext(close_db_session)