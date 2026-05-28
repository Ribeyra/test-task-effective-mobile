import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.models import User
from app.services.permission_service import check_user_permission

router = APIRouter(prefix="/resources", tags=["resources"])

MOCK_DATA = {
    "orders": [
        {"id": "1", "title": "Order #1", "status": "pending"},
        {"id": "2", "title": "Order #2", "status": "shipped"},
    ],
    "products": [
        {"id": "1", "name": "Widget A", "price": 9.99},
        {"id": "2", "name": "Widget B", "price": 14.99},
    ],
    "reports": [
        {"id": "1", "name": "Sales Report Q1", "period": "2025-Q1"},
        {"id": "2", "name": "Sales Report Q2", "period": "2025-Q2"},
    ],
    "users": [
        {"id": "1", "email": "user1@example.com"},
        {"id": "2", "email": "user2@example.com"},
    ],
}


async def _check_resource_access(
    db: AsyncSession, user: User, action: str, resource: str
) -> None:
    has_perm = await check_user_permission(db, user, action, resource)
    if not has_perm:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Forbidden: {action} on {resource}",
        )


@router.get("/{name}")
async def list_resource(
    name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _check_resource_access(db, current_user, "read", name)
    data = MOCK_DATA.get(name, [])
    return {"resource": name, "action": "list", "data": data}


@router.post("/{name}")
async def create_resource(
    name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _check_resource_access(db, current_user, "create", name)
    return {"resource": name, "action": "create", "detail": "Mock created"}


@router.patch("/{name}/{item_id}")
async def update_resource(
    name: str,
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _check_resource_access(db, current_user, "update", name)
    return {"resource": name, "action": "update", "id": item_id, "detail": "Mock updated"}


@router.delete("/{name}/{item_id}")
async def delete_resource(
    name: str,
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _check_resource_access(db, current_user, "delete", name)
    return {"resource": name, "action": "delete", "id": item_id, "detail": "Mock deleted"}
