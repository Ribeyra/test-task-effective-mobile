from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.models import User
from app.schemas.schemas import (
    MessageOut,
    TokenOut,
    UserLogin,
    UserOut,
    UserRegister,
)
from app.services.auth_service import (
    authenticate_user,
    generate_token,
    register_user
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED
)
async def register(body: UserRegister, db: AsyncSession = Depends(get_db)):
    if body.password != body.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )
    try:
        user = await register_user(
            db,
            email=body.email,
            password=body.password,
            first_name=body.first_name,
            last_name=body.last_name,
            middle_name=body.middle_name,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return user


@router.post("/login", response_model=TokenOut)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(
        db, email=body.email, password=body.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = generate_token(user)
    return TokenOut(access_token=token)


@router.post("/logout", response_model=MessageOut)
async def logout(current_user: User = Depends(get_current_user)):
    return MessageOut(detail="Logged out successfully")
