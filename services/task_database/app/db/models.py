import enum
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship

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
    parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    parent = relationship("Task", remote_side=[id], back_populates="subtasks")
    # subtasks = relationship("Task", back_populates="parent")
    subtasks = relationship(
        "Task",
        backref="parent",
        remote_side=[id],
        lazy="joined",
        cascade="all, delete-orphan",
    )

    # # AI-Generated Fields
    complexity = Column(Float, default=0.0)
    priority = Column(Float, default=0.0)
    tags = Column(JSONB, default=list)
    level = Column(Integer, nullable=False, default=0)

    # Multi-tenancy - each task belongs to a user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # user_id = Column(Integer, nullable=True, default=0)

    # Vector for semantic search
    embedding = Column(
        Vector(384), nullable=True
    )  # Dimension depends on embedding model

    # Timestamps
    deadline = Column(DateTime(timezone=True), default=datetime.utcnow)
    start_time_execution = Column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    estimated_duraction = Columt
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
