import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Permission, Resource, Role, User


async def get_permissions_for_user(
    db: AsyncSession, user: User
) -> list[Permission]:
    if user.is_superuser:
        result = await db.execute(select(Permission))
        return list(result.scalars().all())

    role_ids = [role.id for role in user.roles]
    if not role_ids:
        return []

    result = await db.execute(
        select(Permission).where(Permission.role_id.in_(role_ids))
    )
    return list(result.scalars().all())


async def check_user_permission(
    db: AsyncSession, user: User, action: str, resource_name: str
) -> bool:
    if user.is_superuser:
        return True

    role_ids = [role.id for role in user.roles]
    if not role_ids:
        return False

    result = await db.execute(
        select(Resource).where(Resource.name == resource_name)
    )
    resource = result.scalar_one_or_none()
    if not resource:
        return False

    result = await db.execute(
        select(Permission).where(
            Permission.role_id.in_(role_ids),
            Permission.resource_id == resource.id,
        )
    )
    permissions = list(result.scalars().all())
    if not permissions:
        return False

    action_field = f"can_{action}"
    return any(getattr(p, action_field, False) for p in permissions)


async def get_all_roles(db: AsyncSession) -> list[Role]:
    result = await db.execute(select(Role).order_by(Role.name))
    return list(result.scalars().all())


async def get_role_by_id(db: AsyncSession, role_id: uuid.UUID) -> Role | None:
    result = await db.execute(select(Role).where(Role.id == role_id))
    return result.scalar_one_or_none()


async def create_role(
    db: AsyncSession, name: str, description: str | None = None
) -> Role:
    role = Role(name=name, description=description)
    db.add(role)
    await db.flush()
    await db.refresh(role)
    return role


async def update_role(
    db: AsyncSession,
    role: Role,
    name: str | None = None,
    description: str | None = None
) -> Role:
    if name is not None:
        role.name = name
    if description is not None:
        role.description = description
    await db.flush()
    await db.refresh(role)
    return role


async def delete_role(db: AsyncSession, role: Role) -> None:
    await db.delete(role)
    await db.flush()


async def get_all_resources(db: AsyncSession) -> list[Resource]:
    result = await db.execute(select(Resource).order_by(Resource.name))
    return list(result.scalars().all())


async def get_resource_by_id(
    db: AsyncSession, resource_id: uuid.UUID
) -> Resource | None:
    result = await db.execute(select(Resource).where(Resource.id == resource_id))  # noqa e501
    return result.scalar_one_or_none()


async def get_all_permissions(db: AsyncSession) -> list[Permission]:
    result = await db.execute(
        select(Permission).order_by(Permission.role_id, Permission.resource_id)
    )
    return list(result.scalars().all())


async def get_permission_by_id(
    db: AsyncSession, permission_id: uuid.UUID
) -> Permission | None:
    result = await db.execute(
        select(Permission).where(Permission.id == permission_id)
    )
    return result.scalar_one_or_none()


async def create_permission(
    db: AsyncSession,
    role_id: uuid.UUID,
    resource_id: uuid.UUID,
    can_create: bool = False,
    can_read: bool = False,
    can_update: bool = False,
    can_delete: bool = False,
) -> Permission:
    p = Permission(
        role_id=role_id,
        resource_id=resource_id,
        can_create=can_create,
        can_read=can_read,
        can_update=can_update,
        can_delete=can_delete,
    )
    db.add(p)
    await db.flush()
    await db.refresh(p)
    return p


async def update_permission(
    db: AsyncSession,
    permission: Permission,
    **kwargs,
) -> Permission:
    for key, value in kwargs.items():
        if value is not None:
            setattr(permission, key, value)
    await db.flush()
    await db.refresh(permission)
    return permission


async def delete_permission(db: AsyncSession, permission: Permission) -> None:
    await db.delete(permission)
    await db.flush()
