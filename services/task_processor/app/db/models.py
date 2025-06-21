from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from datetime import datetime
import enum

Base = declarative_base()

class TaskStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Task(Base):
    __tablename__ = "tasks"

    # Core Fields
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SAEnum(TaskStatus), nullable=False, default=TaskStatus.PENDING)

    # Tree Structure
    parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    subtasks = relationship("Task", back_populates="parent")
    parent = relationship("Task", remote_side=[id], back_populates="subtasks")

    # AI-Generated Fields
    complexity = Column(Float, default=0.0)
    priority = Column(Float, default=0.0)
    tags = Column(JSONB, default=list)

    # Multi-tenancy - each task belongs to a user
    # user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Vector for semantic search
    embedding = Column(Vector(384), nullable=True) # Dimension depends on embedding model

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)