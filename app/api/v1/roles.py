import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_superuser, get_db
from app.models.models import User
from app.schemas.schemas import MessageOut, RoleCreate, RoleOut, RoleUpdate
from app.services.permission_service import (
    create_role,
    delete_role,
    get_all_roles,
    get_role_by_id,
    update_role,
)

router = APIRouter(prefix="/admin/roles", tags=["admin"])


@router.get("", response_model=list[RoleOut])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    return await get_all_roles(db)


@router.post("", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
async def create_role_endpoint(
    body: RoleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    return await create_role(db, name=body.name, description=body.description)


@router.patch("/{role_id}", response_model=RoleOut)
async def update_role_endpoint(
    role_id: uuid.UUID,
    body: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    role = await get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return await update_role(db, role, name=body.name, description=body.description)


@router.delete("/{role_id}", response_model=MessageOut)
async def delete_role_endpoint(
    role_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    role = await get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete system role",
        )
    await delete_role(db, role)
    return MessageOut(detail="Role deleted successfully")
