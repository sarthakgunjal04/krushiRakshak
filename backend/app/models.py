"""
SQLAlchemy ORM models.

Defines the `User` model used to store authentication information.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    user_type = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    crop = Column(String, nullable=True)  # Primary crop (cotton, wheat, rice, etc.)
    location = Column(String, nullable=True)  # Farm location
    state = Column(String, nullable=True)
    district = Column(String, nullable=True)
    village = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
