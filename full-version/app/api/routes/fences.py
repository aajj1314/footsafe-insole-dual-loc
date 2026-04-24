# -*- coding: utf-8 -*-
"""
电子围栏路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database.session import get_db
from app.api.routes.auth import get_current_user
from app.services.demo_data_service import demo_data_service

router = APIRouter()


class FenceResponse(BaseModel):
    """围栏响应"""
    id: int
    device_imei: str
    name: str
    fence_type: str  # circle, rectangle
    center_lat: Optional[str] = None
    center_lng: Optional[str] = None
    radius: Optional[str] = None  # 圆形围栏半径，单位米
    min_lat: Optional[str] = None  # 矩形围栏南边界
    max_lat: Optional[str] = None  # 矩形围栏北边界
    min_lng: Optional[str] = None  # 矩形围栏西边界
    max_lng: Optional[str] = None  # 矩形围栏东边界
    enabled: bool
    alarm_enabled: bool
    created_at: Optional[str] = None


class FenceListResponse(BaseModel):
    """围栏列表响应"""
    fences: List[FenceResponse]
    total: int


class FenceCreateRequest(BaseModel):
    """创建围栏请求"""
    device_imei: str
    name: str
    fence_type: str = "circle"  # circle, rectangle
    center_lat: Optional[str] = None
    center_lng: Optional[str] = None
    radius: Optional[str] = None
    min_lat: Optional[str] = None
    max_lat: Optional[str] = None
    min_lng: Optional[str] = None
    max_lng: Optional[str] = None
    enabled: bool = True
    alarm_enabled: bool = True


class FenceUpdateRequest(BaseModel):
    """更新围栏请求"""
    name: Optional[str] = None
    center_lat: Optional[str] = None
    center_lng: Optional[str] = None
    radius: Optional[str] = None
    min_lat: Optional[str] = None
    max_lat: Optional[str] = None
    min_lng: Optional[str] = None
    max_lng: Optional[str] = None
    enabled: Optional[bool] = None
    alarm_enabled: Optional[bool] = None


# 简化版围栏存储（实际应该用数据库）
_fences_db: List[dict] = []


@router.get("/", response_model=FenceListResponse)
async def get_fences(
    device_imei: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取电子围栏列表"""
    if demo_data_service.is_demo_user(current_user.id):
        demo_fences = demo_data_service.get_demo_fences()
        if device_imei:
            demo_fences = [f for f in demo_fences if f["device_imei"] == device_imei]
        return FenceListResponse(fences=[FenceResponse(**f) for f in demo_fences], total=len(demo_fences))

    fences = [f for f in _fences_db if f.get("user_id") == current_user.id]
    if device_imei:
        fences = [f for f in fences if f.get("device_imei") == device_imei]
    return FenceListResponse(fences=fences, total=len(fences))


@router.post("/", response_model=FenceResponse)
async def create_fence(
    request: FenceCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建电子围栏"""
    from datetime import datetime
    fence = {
        "id": len(_fences_db) + 1,
        "user_id": current_user.id,
        "device_imei": request.device_imei,
        "name": request.name,
        "fence_type": request.fence_type,
        "center_lat": request.center_lat,
        "center_lng": request.center_lng,
        "radius": request.radius,
        "min_lat": request.min_lat,
        "max_lat": request.max_lat,
        "min_lng": request.min_lng,
        "max_lng": request.max_lng,
        "enabled": request.enabled,
        "alarm_enabled": request.alarm_enabled,
        "created_at": datetime.utcnow().isoformat(),
    }
    _fences_db.append(fence)
    return FenceResponse(**fence)


@router.put("/{fence_id}", response_model=FenceResponse)
async def update_fence(
    fence_id: int,
    request: FenceUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """更新电子围栏"""
    for fence in _fences_db:
        if fence["id"] == fence_id and fence.get("user_id") == current_user.id:
            fence.update({k: v for k, v in request.dict().items() if v is not None})
            return FenceResponse(**fence)
    raise HTTPException(status_code=404, detail="围栏不存在")


@router.delete("/{fence_id}")
async def delete_fence(
    fence_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除电子围栏"""
    for i, fence in enumerate(_fences_db):
        if fence["id"] == fence_id and fence.get("user_id") == current_user.id:
            _fences_db.pop(i)
            return {"message": "删除成功"}
    raise HTTPException(status_code=404, detail="围栏不存在")
