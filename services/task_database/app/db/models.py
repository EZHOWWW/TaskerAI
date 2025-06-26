import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(Base):
    __tablename__ = "tasks"

    # Core Fields
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        SAEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING
    )

    # Tree Structure
    # parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    # subtasks = relationship("Task", back_populates="parent")
    # parent = relationship("Task", remote_side=[id], back_populates="subtasks")

    # # AI-Generated Fields
    complexity = Column(Float, default=0.0)
    priority = Column(Float, default=0.0)
    tags = Column(JSONB, default=list)
    level = Column(Integer, nullable=False, default=0)

    # Multi-tenancy - each task belongs to a user
    # user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_id = Column(Integer, nullable=True, default=0)

    # Vector for semantic search
    # embedding = Column(
    #     Vector(384), nullable=True
    # )  # Dimension depends on embedding model

    # Timestamps
    deadline = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
