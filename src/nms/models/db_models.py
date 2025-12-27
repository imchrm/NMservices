"""Database ORM models."""

from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from nms.database import Base


class User(Base):
    """User table model."""

    __tablename__ = "users"

    # id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id: Mapped[int] = mapped_column(primary_key=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, phone={self.phone_number})>"
