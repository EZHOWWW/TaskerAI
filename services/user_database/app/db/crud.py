from typing import List

from core_lib.models.user import (  # Import Pydantic models
    UserCreate,
    UserUpdate,
)
from passlib.context import CryptContext  # Required for password hashing
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User as DBUser  # Import SQLAlchemy model

# Initialize password hashing context (using bcrypt for strong hashing)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hashes a plain text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)


async def create_user_in_db(
    session: AsyncSession, user_in: UserCreate
) -> DBUser:
    """
    Creates a new user in the database from a Pydantic UserCreate model.
    The password will be hashed before storage.
    """
    hashed_password = get_password_hash(user_in.password)
    db_user = DBUser(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password,
        description=user_in.description_for_llm,
    )
    session.add(db_user)
    await session.commit()  # Commit the transaction to save the user
    await session.refresh(
        db_user
    )  # Refresh to get auto-generated fields like ID and timestamps
    return db_user


async def get_user_by_id(session: AsyncSession, user_id: int) -> DBUser | None:
    """
    Fetches a single user by their unique ID.
    """
    result = await session.execute(select(DBUser).filter(DBUser.id == user_id))
    return result.scalars().first()


async def get_user_by_email(session: AsyncSession, email: str) -> DBUser | None:
    """
    Fetches a single user by their email address.
    """
    result = await session.execute(select(DBUser).filter(DBUser.email == email))
    return result.scalars().first()


async def get_user_by_username(
    session: AsyncSession, username: str
) -> DBUser | None:
    """
    Fetches a single user by their username.
    """
    result = await session.execute(
        select(DBUser).filter(DBUser.username == username)
    )
    return result.scalars().first()


async def get_all_users(
    session: AsyncSession, skip: int = 0, limit: int = 100
) -> List[DBUser]:
    """
    Fetches a list of all users with optional pagination.
    """
    result = await session.execute(select(DBUser).offset(skip).limit(limit))
    return list(result.scalars().all())


async def update_user_in_db(
    session: AsyncSession, db_user: DBUser, user_update: UserUpdate
) -> DBUser:
    """
    Updates an existing user in the database with data from a Pydantic UserUpdate model.
    Only provided fields in user_update will be modified. Password will be re-hashed if provided.
    """
    update_data = user_update.model_dump(
        exclude_unset=True
    )  # Get only explicitly set fields

    # Handle password update: hash if a new password is provided
    if "password" in update_data and update_data["password"] is not None:
        update_data["hashed_password"] = get_password_hash(
            update_data["password"]
        )
        del update_data[
            "password"
        ]  # Remove the plain password from update_data

    # Apply updates to the SQLAlchemy DBUser object
    for key, value in update_data.items():
        if hasattr(db_user, key):  # Ensure the attribute exists on the DB model
            setattr(db_user, key, value)

    # SQLAlchemy's onupdate will automatically handle the 'updated_at' timestamp
    await session.commit()
    await session.refresh(
        db_user
    )  # Refresh to get latest state from DB, including updated_at
    return db_user


async def delete_user_from_db(session: AsyncSession, user_id: int) -> bool:
    """
    Deletes a user from the database by their ID.
    Returns True if the user was found and deleted, False otherwise.
    """
    # Use a DELETE statement for efficiency, rather than loading the object first
    result = await session.execute(delete(DBUser).filter(DBUser.id == user_id))
    await session.commit()  # Commit the deletion
    return result.rowcount > 0  # Check if any row was actually deleted
