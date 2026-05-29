"""seed viewer user with viewer role

Revision ID: 0003
Revises: 0002
Create Date: 2025-01-03
"""
import uuid
from typing import Sequence, Union

from alembic import op
from passlib.context import CryptContext
from sqlalchemy import orm
from sqlalchemy.sql import text

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    result = session.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": "viewer@example.com"},
    )
    if result.fetchone():
        session.close()
        return

    result = session.execute(
        text("SELECT id FROM roles WHERE name = :name"),
        {"name": "viewer"},
    )
    row = result.fetchone()
    if not row:
        session.close()
        return
    viewer_role_id = row[0]

    user_id = uuid.uuid4()
    session.execute(
        text("""
            INSERT INTO users (id, email, password_hash, first_name, last_name, is_active, is_superuser)
            VALUES (:id, :email, :pwd, :fn, :ln, :active, :super)
        """),
        {
            "id": user_id,
            "email": "viewer@example.com",
            "pwd": pwd.hash("viewer123"),
            "fn": "Viewer",
            "ln": "User",
            "active": True,
            "super": False,
        },
    )
    session.execute(
        text("INSERT INTO user_roles (user_id, role_id) VALUES (:uid, :rid)"),
        {"uid": user_id, "rid": viewer_role_id},
    )

    session.commit()
    session.close()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    session.execute(
        text("DELETE FROM users WHERE email = :email"),
        {"email": "viewer@example.com"},
    )
    session.commit()
    session.close()
