from fastapi import FastAPI

from app.api.v1 import admin_users, auth, permissions, resources, roles, users

app = FastAPI(
    title="Auth & Permission System",
    description="Тестовое задание — система аутентификации и авторизации с RBAC/ACL",  # noqa e501
    version="0.1.0",
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(admin_users.router, prefix="/api/v1")
app.include_router(roles.router, prefix="/api/v1")
app.include_router(permissions.router, prefix="/api/v1")
app.include_router(resources.router, prefix="/api/v1")
