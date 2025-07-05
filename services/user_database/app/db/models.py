# user_database/src/db/models.py

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

# Base class for SQLAlchemy declarative models
Base = declarative_base()


class User(Base):
    """SQLAlchemy model for the 'users' table in the database."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(
        String(255), nullable=False
    )  # Stores the hashed password

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    description = Column(Text, nullable=True)

    # Notification info
    tg_username = Column(String(32), unique=True, nullable=True)
    tg_chat_id = Column(Integer, nullable=True)
    is_notified = Column(Boolean, nullable=True)

    # shedule: Optional[UserShedule] = None TODO

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
