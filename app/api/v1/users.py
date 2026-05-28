from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.models import User
from app.schemas.schemas import MessageOut, UserOut, UserUpdate
from app.services.user_service import soft_delete_user, update_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_me(
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = await update_user(
        db,
        current_user,
        first_name=body.first_name,
        last_name=body.last_name,
        middle_name=body.middle_name,
        email=body.email,
    )
    return user


@router.delete("/me", response_model=MessageOut)
async def delete_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await soft_delete_user(db, current_user)
    return MessageOut(detail="Account deleted successfully")
