import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User, UserRole, Role


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_list(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return list(result.scalars().all())


async def update_user(
    db: AsyncSession,
    user: User,
    **kwargs,
) -> User:
    for key, value in kwargs.items():
        if value is not None:
            setattr(user, key, value)
    await db.flush()
    await db.refresh(user)
    return user


async def soft_delete_user(db: AsyncSession, user: User) -> None:
    user.is_active = False
    user.deleted_at = datetime.now(timezone.utc)
    await db.flush()


async def assign_role_to_user(db: AsyncSession, user_id: uuid.UUID, role_id: uuid.UUID) -> None:
    existing = await db.execute(
        select(UserRole).where(
            UserRole.user_id == user_id, UserRole.role_id == role_id
        )
    )
    if existing.scalar_one_or_none():
        return
    user_role = UserRole(user_id=user_id, role_id=role_id)
    db.add(user_role)
    await db.flush()


async def remove_role_from_user(db: AsyncSession, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(UserRole).where(
            UserRole.user_id == user_id, UserRole.role_id == role_id
        )
    )
    user_role = result.scalar_one_or_none()
    if not user_role:
        return False
    await db.delete(user_role)
    await db.flush()
    return True
