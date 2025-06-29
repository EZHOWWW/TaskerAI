from typing import List

from core_lib.models.user import User as PydanticUser
from core_lib.models.user import UserCreate as PydanticUserCreate
from core_lib.models.user import UserUpdate as PydanticUserUpdate
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .core.logging_config import (
    logger,  # Adjust import based on your actual path
)
from .db import crud
from .db.session import get_db_session, init_db

app = FastAPI(
    title="User Database Service",
    description="Provides a data access API for user-related operations, including authentication.",
    version="0.0.1",
)


@app.on_event("startup")
async def on_startup():
    """
    Initializes the database connection and creates tables on application startup.
    """
    logger.info("User database service is starting up...")
    await (
        init_db()
    )  # Call the init_db function to create tables if they don't exist
    logger.info("User database initialized.")


# --- API Endpoints ---


@app.post(
    "/users/", response_model=PydanticUser, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: PydanticUserCreate, session: AsyncSession = Depends(get_db_session)
):
    """
    Register a new user in the database.
    Checks for existing email or username before creation.
    """
    logger.info(f"Received request to create user: {user.username}")

    # Check if user with this email already exists
    db_user_email = await crud.get_user_by_email(session, user.email)
    if db_user_email:
        logger.warning(
            f"User creation failed: Email '{user.email}' already registered."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if user with this username already exists
    db_user_username = await crud.get_user_by_username(session, user.username)
    if db_user_username:
        logger.warning(
            f"User creation failed: Username '{user.username}' already taken."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    try:
        db_user = await crud.create_user_in_db(session=session, user_in=user)
        logger.info(
            f"User created successfully with ID: {db_user.id}, Username: {db_user.username}"
        )
        return PydanticUser.model_validate(db_user)
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user.",
        )


@app.get("/users/{user_id}", response_model=PydanticUser)
async def get_user(
    user_id: int, session: AsyncSession = Depends(get_db_session)
):
    """
    Retrieve a single user by their ID.
    """
    logger.info(f"Received request to retrieve user with ID: {user_id}")
    db_user = await crud.get_user_by_id(session=session, user_id=user_id)
    if db_user is None:
        logger.warning(f"User with ID {user_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    logger.info(
        f"Successfully retrieved user with ID: {user_id}, Username: {db_user.username}"
    )
    return PydanticUser.model_validate(db_user)


@app.get("/users/", response_model=List[PydanticUser])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Retrieve a list of all users with pagination.
    """
    logger.info(
        f"Received request to retrieve users (skip: {skip}, limit: {limit})."
    )
    db_users = await crud.get_all_users(session=session, skip=skip, limit=limit)
    logger.info(f"Retrieved {len(db_users)} users.")
    return [PydanticUser.model_validate(user) for user in db_users]


@app.put("/users/{user_id}", response_model=PydanticUser)
async def update_user(
    user_id: int,
    user_update: PydanticUserUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Update an existing user by their ID.
    Only provided fields will be updated. Password will be re-hashed if updated.
    """
    logger.info(f"Received request to update user with ID: {user_id}")

    db_user = await crud.get_user_by_id(session=session, user_id=user_id)
    if db_user is None:
        logger.warning(
            f"Attempted to update non-existent user with ID: {user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check for email/username conflicts if they are being updated
    if user_update.email and user_update.email != db_user.email:
        existing_user = await crud.get_user_by_email(session, user_update.email)
        if existing_user and existing_user.id != user_id:
            logger.warning(
                f"Update failed: Email '{user_update.email}' already registered by another user."
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    if user_update.username and user_update.username != db_user.username:
        existing_user = await crud.get_user_by_username(
            session, user_update.username
        )
        if existing_user and existing_user.id != user_id:
            logger.warning(
                f"Update failed: Username '{user_update.username}' already taken by another user."
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    try:
        updated_user = await crud.update_user_in_db(
            session=session, db_user=db_user, user_update=user_update
        )
        logger.info(
            f"User with ID: {user_id} updated successfully. Username: {updated_user.username}"
        )
        return PydanticUser.model_validate(updated_user)
    except Exception as e:
        logger.error(
            f"Error updating user with ID {user_id}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user.",
        )


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int, session: AsyncSession = Depends(get_db_session)
):
    """
    Delete a user by their ID.
    Returns 204 No Content on successful deletion.
    """
    logger.info(f"Received request to delete user with ID: {user_id}")
    try:
        success = await crud.delete_user_from_db(
            session=session, user_id=user_id
        )
        if not success:
            logger.warning(
                f"Attempted to delete non-existent user with ID: {user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        logger.info(f"User with ID: {user_id} deleted successfully.")
        return {}  # Return empty dict for 204 No Content
    except Exception as e:
        logger.error(
            f"Error deleting user with ID {user_id}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user.",
        )
