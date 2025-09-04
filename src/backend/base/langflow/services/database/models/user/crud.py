from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from lfx.log.logger import logger
from lfx.services.cache.utils import CacheMiss
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import flag_modified
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from langflow.services.database.models.user.model import User, UserUpdate
from langflow.services.deps import get_cache_service


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    return (await db.exec(stmt)).first()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    if isinstance(user_id, str):
        user_id = UUID(user_id)
    stmt = select(User).where(User.id == user_id)
    return (await db.exec(stmt)).first()


async def get_user_by_id_cached(db: AsyncSession, user_id: UUID) -> User | None:
    """Get user by ID with caching to reduce database contention during JWT validation."""
    if isinstance(user_id, str):
        user_id = UUID(user_id)
    
    # For now, use a simple in-memory cache approach since the cache service is complex
    # This still reduces database contention by avoiding repeated queries for the same user
    cache_key = f"user:{user_id}"
    
    # Use a module-level cache with expiration
    import time
    if not hasattr(get_user_by_id_cached, '_cache'):
        get_user_by_id_cached._cache = {}
        get_user_by_id_cached._cache_times = {}
    
    # Check if we have a cached result that's less than 5 minutes old
    current_time = time.time()
    if (cache_key in get_user_by_id_cached._cache and 
        cache_key in get_user_by_id_cached._cache_times and
        current_time - get_user_by_id_cached._cache_times[cache_key] < 300):  # 5 minutes
        return get_user_by_id_cached._cache[cache_key]
    
    # If not in cache or expired, fetch from database
    stmt = select(User).where(User.id == user_id)
    user = (await db.exec(stmt)).first()
    
    # Cache the result
    get_user_by_id_cached._cache[cache_key] = user
    get_user_by_id_cached._cache_times[cache_key] = current_time
    
    # Clean up old cache entries (keep cache size reasonable)
    if len(get_user_by_id_cached._cache) > 100:
        # Remove entries older than 10 minutes
        cutoff_time = current_time - 600
        keys_to_remove = [
            k for k, t in get_user_by_id_cached._cache_times.items() 
            if t < cutoff_time
        ]
        for k in keys_to_remove:
            get_user_by_id_cached._cache.pop(k, None)
            get_user_by_id_cached._cache_times.pop(k, None)
    
    return user


async def update_user(user_db: User | None, user: UserUpdate, db: AsyncSession) -> User:
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    # user_db_by_username = get_user_by_username(db, user.username)
    # if user_db_by_username and user_db_by_username.id != user_id:
    #     raise HTTPException(status_code=409, detail="Username already exists")

    user_data = user.model_dump(exclude_unset=True)
    changed = False
    for attr, value in user_data.items():
        if hasattr(user_db, attr) and value is not None:
            setattr(user_db, attr, value)
            changed = True

    if not changed:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Nothing to update")

    user_db.updated_at = datetime.now(timezone.utc)
    flag_modified(user_db, "updated_at")

    try:
        await db.commit()
        
        # Invalidate user cache after successful update
        cache_key = f"user:{user_db.id}"
        if hasattr(get_user_by_id_cached, '_cache'):
            get_user_by_id_cached._cache.pop(cache_key, None)
            get_user_by_id_cached._cache_times.pop(cache_key, None)
            
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e

    return user_db


async def update_user_last_login_at(user_id: UUID, db: AsyncSession):
    try:
        user_data = UserUpdate(last_login_at=datetime.now(timezone.utc))
        user = await get_user_by_id(db, user_id)
        return await update_user(user, user_data, db)
    except Exception as e:  # noqa: BLE001
        await logger.aerror(f"Error updating user last login at: {e!s}")


async def get_all_superusers(db: AsyncSession) -> list[User]:
    """Get all superuser accounts from the database."""
    stmt = select(User).where(User.is_superuser == True)  # noqa: E712
    result = await db.exec(stmt)
    return list(result.all())
