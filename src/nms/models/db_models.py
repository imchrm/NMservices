"""Database ORM models."""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, DECIMAL, Text, BigInteger, Boolean
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


class Service(Base):
    """Service table model."""

    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    base_price = Column(DECIMAL(10, 2), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationship
    orders = relationship("Order", back_populates="service")

    def __repr__(self) -> str:
        """String representation of Service."""
        return f"<Service(id={self.id}, name={self.name}, price={self.base_price}, active={self.is_active})>"


class Order(Base):
    """Order table model."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id", ondelete="SET NULL"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    total_amount = Column(DECIMAL(10, 2), nullable=True)
    address_text = Column(Text, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="orders")
    service = relationship("Service", back_populates="orders")

    def __repr__(self) -> str:
        """String representation of Order."""
        return f"<Order(id={self.id}, user_id={self.user_id}, service_id={self.service_id}, status={self.status})>"
