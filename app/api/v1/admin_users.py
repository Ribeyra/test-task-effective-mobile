import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_superuser, get_db
from app.models.models import User
from app.schemas.schemas import (
    AdminUserUpdate,
    AssignRole,
    MessageOut,
    UserOut,
)
from app.services.user_service import (
    assign_role_to_user,
    get_user_by_id,
    get_user_list,
    remove_role_from_user,
    soft_delete_user,
    update_user,
)

router = APIRouter(prefix="/admin/users", tags=["admin"])


@router.get("", response_model=list[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    return await get_user_list(db)


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=UserOut)
async def update_user_admin(
    user_id: uuid.UUID,
    body: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return await update_user(
        db,
        user,
        first_name=body.first_name,
        last_name=body.last_name,
        middle_name=body.middle_name,
        email=body.email,
        is_active=body.is_active,
        is_superuser=body.is_superuser,
    )


@router.delete("/{user_id}", response_model=MessageOut)
async def delete_user_admin(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    await soft_delete_user(db, user)
    return MessageOut(detail="User deleted successfully")


@router.post("/{user_id}/roles", response_model=MessageOut)
async def assign_role(
    user_id: uuid.UUID,
    body: AssignRole,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    await assign_role_to_user(db, user_id, body.role_id)
    return MessageOut(detail="Role assigned successfully")


@router.delete("/{user_id}/roles/{role_id}", response_model=MessageOut)
async def remove_role(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    success = await remove_role_from_user(db, user_id, role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not assigned to user"
        )
    return MessageOut(detail="Role removed successfully")
