from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.dependencies import get_db
from app.models.user import RefreshToken, User, UserProfile
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse

router = APIRouter()
settings = get_settings()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check email/username uniqueness
    existing = await db.execute(
        select(User).where(
            (User.email == request.email) | (User.username == request.username)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already registered",
        )

    user = User(
        email=request.email,
        username=request.username,
        hashed_password=hash_password(request.password),
    )
    db.add(user)
    await db.flush()

    # Create empty profile
    profile = UserProfile(user_id=user.id)
    db.add(profile)
    await db.flush()

    access_token = create_access_token({"sub": user.id})
    refresh_token_str = create_refresh_token({"sub": user.id})

    token_hash = hashlib.sha256(refresh_token_str.encode()).hexdigest()
    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_token)

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token({"sub": user.id})
    refresh_token_str = create_refresh_token({"sub": user.id})

    token_hash = hashlib.sha256(refresh_token_str.encode()).hexdigest()
    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_token)

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_data = decode_refresh_token(request.refresh_token)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    token_hash = hashlib.sha256(request.refresh_token.encode()).hexdigest()
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.is_revoked == False,
        )
    )
    stored_token = result.scalar_one_or_none()
    if not stored_token or stored_token.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    stored_token.is_revoked = True
    new_access = create_access_token({"sub": token_data.user_id})
    new_refresh = create_refresh_token({"sub": token_data.user_id})

    new_hash = hashlib.sha256(new_refresh.encode()).hexdigest()
    db.add(
        RefreshToken(
            user_id=token_data.user_id,
            token_hash=new_hash,
            expires_at=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
    )

    return TokenResponse(access_token=new_access, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_hash = hashlib.sha256(request.refresh_token.encode()).hexdigest()
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    token = result.scalar_one_or_none()
    if token:
        token.is_revoked = True
