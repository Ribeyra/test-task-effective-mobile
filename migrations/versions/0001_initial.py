"""initial: create all tables + seed data

Revision ID: 0001
Revises:
Create Date: 2025-01-01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import orm
from uuid import uuid4
from datetime import datetime, timezone

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("email", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), server_default=""),
        sa.Column("last_name", sa.String(100), server_default=""),
        sa.Column("middle_name", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("is_superuser", sa.Boolean(), server_default="false"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_system", sa.Boolean(), server_default="false"),
    )

    op.create_table(
        "user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "resources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )

    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("role_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("resources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("can_create", sa.Boolean(), server_default="false"),
        sa.Column("can_read", sa.Boolean(), server_default="false"),
        sa.Column("can_update", sa.Boolean(), server_default="false"),
        sa.Column("can_delete", sa.Boolean(), server_default="false"),
    )

    _seed_data()


def _seed_data() -> None:
    from passlib.context import CryptContext
    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    roles_data = {
        "admin": "Full access to all resources",
        "manager": "Can manage orders and products",
        "viewer": "Read-only access to orders, products and reports",
    }
    role_ids = {}
    for name, desc in roles_data.items():
        rid = uuid4()
        session.execute(
            sa.text("INSERT INTO roles (id, name, description, is_system) VALUES (:id, :name, :desc, :sys)"),
            {"id": rid, "name": name, "desc": desc, "sys": name == "admin"},
        )
        role_ids[name] = rid

    resources_data = {
        "orders": "Customer orders",
        "products": "Product catalog",
        "reports": "Business reports",
        "users": "User management",
    }
    resource_ids = {}
    for name, desc in resources_data.items():
        rid = uuid4()
        session.execute(
            sa.text("INSERT INTO resources (id, name, description) VALUES (:id, :name, :desc)"),
            {"id": rid, "name": name, "desc": desc},
        )
        resource_ids[name] = rid

    permissions = [
        ("manager", "orders", True, True, True, False),
        ("manager", "products", True, True, True, False),
        ("viewer", "orders", False, True, False, False),
        ("viewer", "products", False, True, False, False),
        ("viewer", "reports", False, True, False, False),
    ]
    for role_name, res_name, c, r, u, d in permissions:
        session.execute(
            sa.text(
                "INSERT INTO permissions (id, role_id, resource_id, can_create, can_read, can_update, can_delete) "
                "VALUES (:id, :role_id, :res_id, :c, :r, :u, :d)"
            ),
            {
                "id": uuid4(),
                "role_id": role_ids[role_name],
                "res_id": resource_ids[res_name],
                "c": c, "r": r, "u": u, "d": d,
            },
        )

    user_id = uuid4()
    session.execute(
        sa.text(
            "INSERT INTO users (id, email, password_hash, first_name, last_name, is_active, is_superuser, created_at, updated_at) "
            "VALUES (:id, :email, :pwd, :fn, :ln, :active, :super, :now, :now)"
        ),
        {
            "id": user_id,
            "email": "admin@example.com",
            "pwd": pwd.hash("admin123"),
            "fn": "Admin",
            "ln": "Adminov",
            "active": True,
            "super": True,
            "now": datetime.now(timezone.utc),
        },
    )
    session.execute(
        sa.text("INSERT INTO user_roles (user_id, role_id) VALUES (:uid, :rid)"),
        {"uid": user_id, "rid": role_ids["admin"]},
    )

    session.commit()
    session.close()


def downgrade() -> None:
    op.drop_table("permissions")
    op.drop_table("user_roles")
    op.drop_table("resources")
    op.drop_table("roles")
    op.drop_table("users")
