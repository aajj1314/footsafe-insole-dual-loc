# -*- coding: utf-8 -*-
"""
用户服务模块
"""

import hashlib
import secrets
from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.orm.user import User
from app.core.logger import logger


class UserService:
    """用户服务"""

    def __init__(self, session: AsyncSession):
        """
        初始化用户服务

        Args:
            session: 数据库会话
        """
        self.session = session

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        哈希密码

        Args:
            password: 明文密码
            salt: 盐值，不提供则自动生成

        Returns:
            (哈希后的密码, 盐值)
        """
        if salt is None:
            salt = secrets.token_hex(16)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000,
        )
        return password_hash.hex(), salt

    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """
        验证密码

        Args:
            password: 明文密码
            password_hash: 存储的密码哈希
            salt: 盐值

        Returns:
            是否验证通过
        """
        computed_hash, _ = UserService.hash_password(password, salt)
        return computed_hash == password_hash

    async def create_user(
        self,
        username: str,
        password: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Optional[User]:
        """
        创建用户

        Args:
            username: 用户名
            password: 明文密码
            phone: 手机号
            email: 邮箱

        Returns:
            创建的用户对象，失败返回None
        """
        try:
            # 检查用户名是否已存在
            existing = await self.get_by_username(username)
            if existing:
                logger.warning(f"Username already exists: {username}")
                return None

            # 哈希密码
            password_hash, salt = self.hash_password(password)

            # 创建用户
            user = User(
                username=username,
                password_hash=f"{password_hash}${salt}",
                phone=phone,
                email=email,
                status="active",
            )

            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)

            logger.info(f"User created: {username}")
            return user

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to create user: {e}")
            return None

    async def authenticate(
        self, username: str, password: str
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        用户认证

        Args:
            username: 用户名
            password: 明文密码

        Returns:
            (用户对象, 错误信息)
        """
        user = await self.get_by_username(username)
        if not user:
            return None, "用户名或密码错误"

        if user.status != "active":
            return None, "账号已被禁用"

        # 解析存储的密码哈希
        try:
            password_hash, salt = user.password_hash.split("$")
        except ValueError:
            return None, "密码格式错误"

        if not self.verify_password(password, password_hash, salt):
            return None, "用户名或密码错误"

        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        await self.session.commit()

        return user, None

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        通过用户名获取用户

        Args:
            username: 用户名

        Returns:
            用户对象
        """
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        通过ID获取用户

        Args:
            user_id: 用户ID

        Returns:
            用户对象
        """
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_user(
        self,
        user_id: int,
        nickname: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        avatar: Optional[str] = None,
    ) -> bool:
        """
        更新用户信息

        Args:
            user_id: 用户ID
            nickname: 昵称
            phone: 手机号
            email: 邮箱
            avatar: 头像URL

        Returns:
            是否更新成功
        """
        try:
            updates = {}
            if nickname is not None:
                updates["nickname"] = nickname
            if phone is not None:
                updates["phone"] = phone
            if email is not None:
                updates["email"] = email
            if avatar is not None:
                updates["avatar"] = avatar

            if updates:
                updates["updated_at"] = datetime.utcnow()
                await self.session.execute(
                    update(User).where(User.id == user_id).values(**updates)
                )
                await self.session.commit()

            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to update user: {e}")
            return False

    async def ensure_demo_user(self, username: str = "admin", password: str = "admin") -> bool:
        """
        确保演示账号存在，不影响其他用户

        Args:
            username: 演示用户名
            password: 演示密码

        Returns:
            是否成功（账号已存在或创建成功）
        """
        try:
            existing = await self.get_by_username(username)
            if existing:
                logger.info(f"Demo user '{username}' already exists")
                return True

            password_hash, salt = self.hash_password(password)
            demo_user = User(
                username=username,
                password_hash=f"{password_hash}${salt}",
                phone="13800138000",
                email="admin@zu-an.demo",
                nickname="演示管理员",
                status="active",
            )
            self.session.add(demo_user)
            await self.session.commit()
            logger.info(f"Demo user '{username}' created successfully")
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to ensure demo user: {e}")
            return False
