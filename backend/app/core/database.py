"""
Database engine, session factory, and base model.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
import ssl as _ssl

# Build connect_args for asyncpg when using PostgreSQL with sslmode
_db_url = settings.DATABASE_URL
_connect_args: dict = {}

if "asyncpg" in _db_url and "sslmode=" in _db_url:
    # asyncpg uses 'ssl' instead of 'sslmode'; strip it from the URL
    # and pass a proper SSL context via connect_args
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

    parsed = urlparse(_db_url)
    params = parse_qs(parsed.query)
    params.pop("sslmode", None)
    clean_query = urlencode(params, doseq=True)
    _db_url = urlunparse(parsed._replace(query=clean_query))

    ssl_ctx = _ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = _ssl.CERT_NONE
    _connect_args = {"ssl": ssl_ctx}

# Create async engine
engine = create_async_engine(
    _db_url,
    echo=settings.DEBUG,
    future=True,
    connect_args=_connect_args,
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""
    pass


async def get_db():
    """FastAPI dependency that yields a database session.

    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables (for development). Use Alembic in production."""
    # Import models here to register them with Base.metadata, avoiding circular imports
    from app.models.user import User
    from app.models.analysis import ResumeAnalysis
    from app.models.skill import SkillResult

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

