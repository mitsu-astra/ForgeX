"""
PostgreSQL Database Session and Connection Management for Industrial AI
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.config import settings

logger = logging.getLogger("backend.db.session")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://industrial_user:localdev123@localhost:5432/industrial_ai"
)

# Create synchronous engine with connection pooling
try:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )
    logger.info(f"[DB] Initialized PostgreSQL engine with URL: {DATABASE_URL}")
except Exception as e:
    logger.error(f"[DB] Failed to initialize PostgreSQL engine: {e}")
    # Fallback to postgres default user if local user fails
    alt_url = "postgresql://postgres:postgres@localhost:5432/industrial_ai"
    engine = create_engine(alt_url, pool_size=5, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
