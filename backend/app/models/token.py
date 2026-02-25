from sqlalchemy import Column, String, Integer, DateTime, func
from app.models.database import Base


class DeviceUsage(Base):
    __tablename__ = "device_usage"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, nullable=False, index=True)
    scans_today = Column(Integer, default=0)
    last_scan_date = Column(String, nullable=True)  # YYYY-MM-DD
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class GenerationToken(Base):
    __tablename__ = "generation_tokens"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, nullable=False, index=True)
    tokens_remaining = Column(Integer, default=0)
    tokens_total = Column(Integer, default=0)
    product_sku = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    checkout_id = Column(String, unique=True, nullable=False)
    device_id = Column(String, nullable=False)
    product_sku = Column(String, nullable=False)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, default="pending")
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
