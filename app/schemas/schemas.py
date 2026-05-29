import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    password_confirm: str = Field(min_length=6)
    first_name: str = ""
    last_name: str = ""
    middle_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    middle_name: str | None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None


class AdminUserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class RoleOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    is_system: bool

    model_config = {"from_attributes": True}


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ResourceOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None

    model_config = {"from_attributes": True}


class PermissionCreate(BaseModel):
    role_id: uuid.UUID
    resource_id: uuid.UUID
    can_create: bool = False
    can_read: bool = False
    can_update: bool = False
    can_delete: bool = False


class PermissionOut(BaseModel):
    id: uuid.UUID
    role_id: uuid.UUID
    resource_id: uuid.UUID
    can_create: bool
    can_read: bool
    can_update: bool
    can_delete: bool
    role: RoleOut | None = None
    resource: ResourceOut | None = None

    model_config = {"from_attributes": True}


class PermissionUpdate(BaseModel):
    can_create: bool | None = None
    can_read: bool | None = None
    can_update: bool | None = None
    can_delete: bool | None = None


class AssignRole(BaseModel):
    role_id: uuid.UUID


class MessageOut(BaseModel):
    detail: str
