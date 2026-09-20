"""
PostgreSQL Database Session and Connection Management for ForgeX • Industrial Decision Intelligence
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

# Create synchronous engine with graceful SQLite fallback if PostgreSQL is offline
try:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
    )
    with engine.connect() as conn:
        pass
    logger.info(f"[DB] Connected to PostgreSQL: {DATABASE_URL}")
except Exception as e:
    logger.warning(f"[DB] PostgreSQL connection failed ({e}). Falling back to local SQLite database.")
    sqlite_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "industrial_ai.db")
    engine = create_engine(f"sqlite:///{sqlite_db_path}", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
