# Database configuration and connection management
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from typing import Generator
import asyncpg
from contextlib import asynccontextmanager

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/physical_ai_book")
NEON_DATABASE_URL = os.getenv("NEON_DATABASE_URL", DATABASE_URL)

# Use Neon database URL if available, otherwise fall back to local
ACTIVE_DATABASE_URL = NEON_DATABASE_URL if NEON_DATABASE_URL != DATABASE_URL else DATABASE_URL

# SQLAlchemy setup
engine = create_engine(
    ACTIVE_DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("DEBUG", "false").lower() == "true"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import Base from models to ensure consistency
from .models.user import Base

# Dependency to get database session
def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Async database connection for advanced operations
@asynccontextmanager
async def get_async_db():
    """
    Async context manager for database connections.
    Useful for operations that need async database access.
    """
    conn = None
    try:
        conn = await asyncpg.connect(ACTIVE_DATABASE_URL)
        yield conn
    finally:
        if conn:
            await conn.close()

# Database initialization
def init_db():
    """
    Initialize database tables.
    Creates all tables defined in the models.
    """
    # Import all models to ensure they are registered
    from .models import user  # noqa
    
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

# Health check for database
def check_db_health() -> bool:
    """
    Check if database connection is healthy.
    Returns True if connection is successful, False otherwise.
    """
    try:
        db = SessionLocal()
        # Simple query to test connection
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False

# Database utilities
class DatabaseManager:
    """Database management utilities."""
    
    @staticmethod
    def create_tables():
        """Create all database tables."""
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def drop_tables():
        """Drop all database tables. Use with caution!"""
        Base.metadata.drop_all(bind=engine)
    
    @staticmethod
    def reset_database():
        """Reset database by dropping and recreating all tables."""
        DatabaseManager.drop_tables()
        DatabaseManager.create_tables()
    
    @staticmethod
    def get_table_info():
        """Get information about database tables."""
        inspector = engine.inspect(engine)
        tables = inspector.get_table_names()
        return {
            "tables": tables,
            "total_tables": len(tables)
        }