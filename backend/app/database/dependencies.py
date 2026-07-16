"""Database session dependency for FastAPI."""

from typing import Generator

from sqlalchemy.orm import Session

from app.database.session import SessionLocal


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency for getting a database session.
    
    Automatically closes session after request.
    
    Usage:
        @app.get("/items")
        async def get_items(db: Session = Depends(get_db_session)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
