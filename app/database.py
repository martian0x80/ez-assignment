from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
import os

# Create database engine
# Use test database if TESTING environment variable is set
if os.getenv("TESTING"):
    database_url = "sqlite:///./test.db"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(settings.database_url)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
