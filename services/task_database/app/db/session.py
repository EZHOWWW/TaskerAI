from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .models import Base  # Import Base from our db models

# Create an asynchronous engine to connect to the database
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Create a factory for asynchronous sessions
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """
    Initialize the database and create tables if they don't exist.
    Should be called on application startup.
    """
    async with engine.begin() as conn:
        # This will create all tables defined in models that inherit from Base
        # In a production environment, you would use Alembic for migrations.
        await conn.run_sync(Base.metadata.create_all)


async def get_db_session() -> AsyncSession:
    """
    FastAPI dependency to get a database session.
    Ensures the session is always closed after the request.
    """
    async with AsyncSessionLocal() as session:
        yield session
