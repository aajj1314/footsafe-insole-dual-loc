# -*- coding: utf-8 -*-
"""
联系人路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.session import get_db
from app.api.routes.auth import get_current_user

router = APIRouter()


class ContactResponse(BaseModel):
    """联系人响应"""
    id: int
    name: str
    phone: str
    relation: str
    is_primary: bool
    created_at: str


class ContactCreateRequest(BaseModel):
    """创建联系人请求"""
    name: str
    phone: str
    relation: str
    is_primary: bool = False


class ContactUpdateRequest(BaseModel):
    """更新联系人请求"""
    name: str
    phone: str
    relation: str
    is_primary: bool


# 简化版联系人存储（实际应该用数据库）
_contacts_db: List[dict] = []


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    current_user: dict = Depends(get_current_user)
):
    """获取联系人列表"""
    contacts = [c for c in _contacts_db if c.get("user_id") == current_user.id]
    return contacts


@router.post("/", response_model=ContactResponse)
async def create_contact(
    request: ContactCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """添加联系人"""
    from datetime import datetime
    contact = {
        "id": len(_contacts_db) + 1,
        "user_id": current_user.id,
        "name": request.name,
        "phone": request.phone,
        "relation": request.relation,
        "is_primary": request.is_primary,
        "created_at": datetime.utcnow().isoformat(),
    }
    _contacts_db.append(contact)
    return ContactResponse(**contact)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    request: ContactUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """更新联系人"""
    from datetime import datetime
    for contact in _contacts_db:
        if contact["id"] == contact_id and contact.get("user_id") == current_user.id:
            contact["name"] = request.name
            contact["phone"] = request.phone
            contact["relation"] = request.relation
            contact["is_primary"] = request.is_primary
            contact["created_at"] = contact.get("created_at", datetime.utcnow().isoformat())
            return ContactResponse(**contact)
    raise HTTPException(status_code=404, detail="联系人不存在")


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除联系人"""
    for i, contact in enumerate(_contacts_db):
        if contact["id"] == contact_id and contact.get("user_id") == current_user.id:
            _contacts_db.pop(i)
            return {"message": "删除成功"}
    raise HTTPException(status_code=404, detail="联系人不存在")
