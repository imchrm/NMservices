"""Database ORM models."""

from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, DECIMAL, Text, BigInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from nms.database import Base


class OrderStatus(str, PyEnum):
    """Valid order statuses."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, PyEnum):
    """Valid payment statuses."""

    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"


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
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=OrderStatus.PENDING, index=True)
    notified_status = Column(String(50), nullable=True, default=None)
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

    payment = relationship("Payment", back_populates="order", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of Order."""
        return f"<Order(id={self.id}, user_id={self.user_id}, service_id={self.service_id}, status={self.status})>"


class Payment(Base):
    """Payment table model."""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=PaymentStatus.PENDING, index=True)
    provider = Column(String(50), nullable=False, default="payme_demo")
    token = Column(String(64), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    order = relationship("Order", back_populates="payment")

    def __repr__(self) -> str:
        """String representation of Payment."""
        return f"<Payment(id={self.id}, order_id={self.order_id}, status={self.status}, provider={self.provider})>"
