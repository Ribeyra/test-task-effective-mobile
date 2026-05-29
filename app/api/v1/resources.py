"""
Mock-эндпоинты для демонстрации системы разграничения доступа.

Роуты /resources/orders — явные, используют check_permission().
Это эталонный вариант: ресурс известен на этапе импорта,
Depends(check_permission(...)) работает прозрачно.

Остальные роуты (/resources/{name}) — универсальные, с ручной проверкой
прав внутри хендлера (_check_resource_access), чтобы не плодить код
для каждого ресурса в рамках тестового задания.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import check_permission, get_current_user, get_db
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


# ── orders — эталонные явные роуты с check_permission ──

@router.get("/orders")
async def list_orders(
    _: User = Depends(check_permission("read", "orders")),
):
    return {
        "resource": "orders", "action": "list", "data": MOCK_DATA["orders"]
    }


@router.post("/orders")
async def create_orders(
    _: User = Depends(check_permission("create", "orders")),
):
    return {"resource": "orders", "action": "create", "detail": "Mock created"}


@router.patch("/orders/{item_id}")
async def update_orders(
    item_id: str,
    _: User = Depends(check_permission("update", "orders")),
):
    return {
        "resource": "orders",
        "action": "update",
        "id": item_id,
        "detail": "Mock updated"
    }


@router.delete("/orders/{item_id}")
async def delete_orders(
    item_id: str,
    _: User = Depends(check_permission("delete", "orders")),
):
    return {
        "resource": "orders",
        "action": "delete",
        "id": item_id,
        "detail": "Mock deleted"
    }


# ── универсальные роуты для остальных ресурсов ──

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
    return {
        "resource": name,
        "action": "update",
        "id": item_id,
        "detail": "Mock updated"
    }


@router.delete("/{name}/{item_id}")
async def delete_resource(
    name: str,
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _check_resource_access(db, current_user, "delete", name)
    return {
        "resource": name,
        "action": "delete",
        "id": item_id,
        "detail": "Mock deleted"
    }
