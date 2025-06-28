import enum
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Interval,
    String,
    Text,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship

# from .embedding import EMBEDDING_SIZE

EMBEDDING_SIZE = 384


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

    # Defines the "one-to-many" relationship for subtasks.
    # When a parent task is deleted, all its subtasks are also deleted due to the cascade.
    subtasks = relationship(
        "Task",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin",  # Efficiently loads subtasks
    )

    # Defines the "many-to-one" relationship for the parent.
    # remote_side is required for self-referential relationships.
    parent = relationship("Task", back_populates="subtasks", remote_side=[id])

    # AI-Generated Fields
    complexity = Column(Float, default=0.0)
    priority = Column(Float, default=0.0)
    tags = Column(JSONB, default=list)
    level = Column(Integer, nullable=False, default=0)

    # Multi-tenancy - each task belongs to a user
    # user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_id = Column(Integer, nullable=True, default=0)

    # Vector for semantic search
    embedding = Column(
        Vector(EMBEDDING_SIZE), nullable=True
    )  # Dimension depends on embedding model

    # Timestamps
    deadline = Column(DateTime(timezone=True), default=datetime.utcnow)
    start_time_execution = Column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    estimated_duraction = Column(Interval, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
