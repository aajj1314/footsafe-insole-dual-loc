# -*- coding: utf-8 -*-
"""
认证路由
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db
from app.services.user_service import UserService
from app.core.security.jwt import create_access_token, verify_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None
    email: Optional[str] = None


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    nickname: Optional[str] = None
    created_at: Optional[str] = None
    last_login: Optional[str] = None


class AuthResponse(BaseModel):
    """认证响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """获取当前用户"""
    from app.services.demo_data_service import demo_data_service

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    # 演示用户直接返回预设信息
    if demo_data_service.is_demo_user(user_id):
        return UserResponse(
            id=demo_data_service.DEMO_USER_ID,
            username="admin",
            phone="13800138000",
            email="admin@zu-an.demo",
            nickname="演示管理员",
            created_at="2026-04-19T12:40:58.832245",
            last_login=None,
        )

    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise credentials_exception

    return UserResponse(
        id=user.id,
        username=user.username,
        phone=user.phone,
        email=user.email,
        avatar=user.avatar,
        nickname=user.nickname,
        created_at=user.created_at.isoformat() if user.created_at else None,
        last_login=user.last_login.isoformat() if user.last_login else None,
    )


@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    user_service = UserService(db)

    # 检查用户名是否存在
    existing_user = await user_service.get_by_username(request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 创建用户
    user = await user_service.create_user(
        username=request.username,
        password=request.password,
        phone=request.phone,
        email=request.email,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建用户失败"
        )

    # 生成Token
    access_token = create_access_token(data={"sub": user.id})

    return AuthResponse(
        access_token=access_token,
        user=UserResponse(
            id=user.id,
            username=user.username,
            phone=user.phone,
            email=user.email,
            created_at=user.created_at.isoformat() if user.created_at else None,
        )
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    from app.services.demo_data_service import demo_data_service

    user_service = UserService(db)

    # 验证用户
    user, error = await user_service.authenticate(request.username, request.password)
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
        )

    # 演示账号使用固定ID
    user_id = user.id
    if demo_data_service.is_demo_username(request.username):
        user_id = demo_data_service.DEMO_USER_ID

    # 生成Token
    access_token = create_access_token(data={"sub": user_id})

    return AuthResponse(
        access_token=access_token,
        user=UserResponse(
            id=user_id,
            username=user.username,
            phone=user.phone,
            email=user.email,
            avatar=user.avatar,
            nickname=user.nickname,
            created_at=user.created_at.isoformat() if user.created_at else None,
            last_login=user.last_login.isoformat() if user.last_login else None,
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """退出登录"""
    return {"message": "退出成功"}
