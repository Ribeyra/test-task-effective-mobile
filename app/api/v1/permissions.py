import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_superuser, get_db
from app.models.models import User
from app.schemas.schemas import (
    MessageOut,
    PermissionCreate,
    PermissionOut,
    PermissionUpdate,
)
from app.services.permission_service import (
    create_permission,
    delete_permission,
    get_all_permissions,
    get_permission_by_id,
    update_permission,
)

router = APIRouter(prefix="/admin/permissions", tags=["admin"])


@router.get("", response_model=list[PermissionOut])
async def list_permissions(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    return await get_all_permissions(db)


@router.post(
    "", response_model=PermissionOut, status_code=status.HTTP_201_CREATED
)
async def create_permission_endpoint(
    body: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    return await create_permission(
        db,
        role_id=body.role_id,
        resource_id=body.resource_id,
        can_create=body.can_create,
        can_read=body.can_read,
        can_update=body.can_update,
        can_delete=body.can_delete,
    )


@router.patch("/{permission_id}", response_model=PermissionOut)
async def update_permission_endpoint(
    permission_id: uuid.UUID,
    body: PermissionUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    permission = await get_permission_by_id(db, permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return await update_permission(
        db,
        permission,
        can_create=body.can_create,
        can_read=body.can_read,
        can_update=body.can_update,
        can_delete=body.can_delete,
    )


@router.delete("/{permission_id}", response_model=MessageOut)
async def delete_permission_endpoint(
    permission_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    permission = await get_permission_by_id(db, permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    await delete_permission(db, permission)
    return MessageOut(detail="Permission deleted successfully")
