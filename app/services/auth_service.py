from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    hash_password,
    hash_token,
    verify_password
)
from app.models.models import Role, User, UserRole


async def register_user(
    db: AsyncSession,
    email: str,
    password: str,
    first_name: str = "",
    last_name: str = "",
    middle_name: str | None = None,
) -> User:
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise ValueError("Email already registered")

    user = User(
        email=email,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    result = await db.execute(select(Role).where(Role.name == "viewer"))
    viewer_role = result.scalar_one_or_none()
    if viewer_role:
        db.add(UserRole(user_id=user.id, role_id=viewer_role.id))
        await db.flush()

    return user


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def generate_token(user: User) -> str:
    token = create_access_token({"sub": str(user.id)})
    user.current_token_hash = hash_token(token)
    return token


async def clear_user_token(db: AsyncSession, user: User) -> None:
    user.current_token_hash = None
    await db.flush()
