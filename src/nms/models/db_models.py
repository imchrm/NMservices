"""Database ORM models."""

from datetime import datetime
# from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, DECIMAL, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from nms.database import Base


class User(Base):
    """User table model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=True, index=True)
    language_code = Column(String(5), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationship
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, phone={self.phone_number}, telegram_id={self.telegram_id}, lang={self.language_code})>"


class Order(Base):
    """Order table model."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    total_amount = Column(DECIMAL(10, 2), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationship
    user = relationship("User", back_populates="orders")

    def __repr__(self) -> str:
        """String representation of Order."""
        return f"<Order(id={self.id}, user_id={self.user_id}, status={self.status})>"
