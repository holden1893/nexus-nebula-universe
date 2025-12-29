"""NEXUS NEBULA MARKETPLACE - Database Models

Minimal async-SQLAlchemy models for a marketplace economy.

Notes:
- Uses JSON columns for tags/media for simplicity.
- SQLite support is fine for local/dev. For production, swap to Postgres.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class LicenseType(str, Enum):
    MIT = "MIT"
    COMMERCIAL = "commercial"
    PERSONAL = "personal"
    CUSTOM = "custom"


class ListingStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    SOLD_OUT = "sold_out"
    REMOVED = "removed"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)

    wallet_balance = Column(Float, default=0.0)
    total_earnings = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)

    seller_rating = Column(Float, default=5.0)
    total_sales = Column(Integer, default=0)

    stripe_customer_id = Column(String)
    stripe_account_id = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    listings = relationship("Listing", back_populates="seller")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False)
    seller_id = Column(String, ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    license_type = Column(String, nullable=False)

    tags = Column(JSON)
    category = Column(String)

    current_sales = Column(Integer, default=0)
    max_sales = Column(Integer)

    views = Column(Integer, default=0)
    rating = Column(Float, default=5.0)
    review_count = Column(Integer, default=0)

    status = Column(String, default=ListingStatus.DRAFT.value)
    preview_images = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime)

    seller = relationship("User", back_populates="listings")
    transactions = relationship("Transaction", back_populates="listing")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    buyer_id = Column(String, ForeignKey("users.id"), nullable=False)
    seller_id = Column(String, ForeignKey("users.id"), nullable=False)
    listing_id = Column(String, ForeignKey("listings.id"), nullable=False)

    amount = Column(Float, nullable=False)
    platform_fee = Column(Float, nullable=False)
    seller_payout = Column(Float, nullable=False)

    stripe_payment_id = Column(String)
    license_key = Column(String)

    status = Column(String, default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

    listing = relationship("Listing", back_populates="transactions")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True)
    listing_id = Column(String, ForeignKey("listings.id"), nullable=False)
    buyer_id = Column(String, ForeignKey("users.id"), nullable=False)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)

    rating = Column(Integer, nullable=False)
    title = Column(String)
    comment = Column(Text)

    verified_purchase = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
