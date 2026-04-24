# -*- coding: utf-8 -*-
"""
位置路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database.session import get_db
from app.api.routes.auth import get_current_user
from app.models.orm.device import Device
from app.models.orm.user_device import UserDevice
from app.services.demo_data_service import demo_data_service

router = APIRouter()


class LocationResponse(BaseModel):
    """位置响应"""
    latitude: str
    longitude: str
    altitude: Optional[str] = None
    speed: Optional[str] = None
    direction: Optional[str] = None
    accuracy: Optional[str] = None
    satellites: Optional[int] = None
    battery: Optional[int] = None
    signal_strength: Optional[int] = None
    mode: Optional[str] = None
    gps_timestamp: Optional[str] = None
    created_at: Optional[str] = None


class LocationHistoryResponse(BaseModel):
    """历史位置响应"""
    locations: List[LocationResponse]
    total: int


@router.get("/{device_imei}/latest", response_model=LocationResponse)
async def get_latest_location(
    device_imei: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取设备最新位置"""
    user_id = current_user.id

    if demo_data_service.is_demo_user(user_id):
        demo_locations = demo_data_service.get_demo_locations(device_imei)
        if demo_locations:
            return LocationResponse(**demo_locations[0])
        raise HTTPException(status_code=404, detail="暂无位置数据")

    # 验证设备归属
    result = await db.execute(
        select(Device)
        .join(UserDevice, UserDevice.device_id == Device.id)
        .where(
            Device.imei == device_imei,
            UserDevice.user_id == user_id,
            UserDevice.status == "active"
        )
    )
    device = result.scalar_one_or_none()

    if device is None:
        raise HTTPException(status_code=404, detail="设备不存在或无权访问")

    if not device.last_location_lat or not device.last_location_lng:
        raise HTTPException(status_code=404, detail="暂无位置数据")

    return LocationResponse(
        latitude=device.last_location_lat,
        longitude=device.last_location_lng,
        altitude=device.last_location_alt,
        speed=device.last_location_speed,
        direction=device.last_location_direction,
        accuracy=device.last_location_accuracy,
        satellites=device.satellites,
        battery=device.battery,
        signal_strength=device.signal_strength,
        mode=device.mode,
        gps_timestamp=device.last_location_time.isoformat() if device.last_location_time else None,
        created_at=device.last_location_time.isoformat() if device.last_location_time else None,
    )


@router.get("/{device_imei}/history", response_model=LocationHistoryResponse)
async def get_location_history(
    device_imei: str,
    start_time: Optional[str] = Query(None, description="开始时间 ISO格式"),
    end_time: Optional[str] = Query(None, description="结束时间 ISO格式"),
    limit: int = Query(100, le=500),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取设备历史轨迹"""
    user_id = current_user.id

    if demo_data_service.is_demo_user(user_id):
        demo_locations = demo_data_service.get_demo_locations(device_imei)
        return LocationHistoryResponse(
            locations=[LocationResponse(**loc) for loc in demo_locations[:limit]],
            total=len(demo_locations)
        )

    # 验证设备归属
    result = await db.execute(
        select(Device)
        .join(UserDevice, UserDevice.device_id == Device.id)
        .where(
            Device.imei == device_imei,
            UserDevice.user_id == user_id,
            UserDevice.status == "active"
        )
    )
    device = result.scalar_one_or_none()

    if device is None:
        raise HTTPException(status_code=404, detail="设备不存在或无权访问")

    # 返回设备当前位置作为历史（简化版）
    if device.last_location_lat:
        locations = [LocationResponse(
            latitude=device.last_location_lat,
            longitude=device.last_location_lng,
            altitude=device.last_location_alt,
            speed=device.last_location_speed,
            direction=device.last_location_direction,
            accuracy=device.last_location_accuracy,
            gps_timestamp=device.last_location_time.isoformat() if device.last_location_time else None,
            created_at=device.last_location_time.isoformat() if device.last_location_time else None,
        )]
    else:
        locations = []

    return LocationHistoryResponse(locations=locations, total=len(locations))
