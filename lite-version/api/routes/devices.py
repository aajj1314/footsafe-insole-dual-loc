# -*- coding: utf-8 -*-
"""
设备路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database.session import get_db
from app.api.routes.auth import get_current_user
from app.models.orm.device import Device
from app.models.orm.user_device import UserDevice
from app.services.demo_data_service import demo_data_service

router = APIRouter()


class DeviceBindRequest(BaseModel):
    """绑定设备请求"""
    device_imei: str = Field(..., min_length=15, max_length=15)
    nickname: Optional[str] = None
    relation: Optional[str] = None


class DeviceResponse(BaseModel):
    """设备响应"""
    id: int
    imei: str
    nickname: Optional[str] = None
    relation: Optional[str] = None
    iccid: Optional[str] = None
    firmware_version: Optional[str] = None
    hardware_version: Optional[str] = None
    battery: Optional[int] = None
    signal_strength: Optional[int] = None
    mode: Optional[str] = None
    status: Optional[str] = None
    last_location_lat: Optional[str] = None
    last_location_lng: Optional[str] = None
    last_location_time: Optional[str] = None
    created_at: Optional[str] = None


class DeviceListResponse(BaseModel):
    """设备列表响应"""
    devices: List[DeviceResponse]
    total: int


@router.post("/bind", response_model=DeviceResponse)
async def bind_device(
    request: DeviceBindRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """绑定设备到当前用户"""
    user_id = current_user.id

    # 检查设备是否存在
    result = await db.execute(select(Device).where(Device.imei == request.device_imei))
    device = result.scalar_one_or_none()

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备未注册，请先在设备端注册"
        )

    # 检查是否已经绑定到其他用户
    result = await db.execute(
        select(UserDevice).where(
            UserDevice.device_id == device.id,
            UserDevice.status == "active"
        )
    )
    existing_binding = result.scalar_one_or_none()

    if existing_binding and existing_binding.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="设备已被其他用户绑定"
        )

    if existing_binding and existing_binding.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="设备已经绑定到您的账户"
        )

    # 创建绑定关系
    user_device = UserDevice(
        user_id=user_id,
        device_id=device.id,
        nickname=request.nickname,
        relation=request.relation,
        status="active"
    )

    db.add(user_device)
    await db.commit()

    return DeviceResponse(
        id=device.id,
        imei=device.imei,
        nickname=request.nickname,
        relation=request.relation,
        iccid=device.iccid,
        firmware_version=device.firmware_version,
        hardware_version=device.hardware_version,
        battery=device.battery,
        signal_strength=device.signal_strength,
        mode=device.mode,
        status=device.status,
        last_location_lat=device.last_location_lat,
        last_location_lng=device.last_location_lng,
        last_location_time=device.last_location_time.isoformat() if device.last_location_time else None,
        created_at=device.created_at.isoformat() if device.created_at else None,
    )


@router.get("/", response_model=DeviceListResponse)
async def get_devices(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户的所有设备"""
    user_id = current_user.id

    if demo_data_service.is_demo_user(user_id):
        demo_devices = demo_data_service.get_demo_devices()
        return DeviceListResponse(
            devices=[DeviceResponse(**d) for d in demo_devices],
            total=len(demo_devices)
        )

    # 查询用户绑定的设备
    result = await db.execute(
        select(UserDevice, Device)
        .join(Device, UserDevice.device_id == Device.id)
        .where(UserDevice.user_id == user_id, UserDevice.status == "active")
    )
    rows = result.all()

    devices = []
    for user_device, device in rows:
        devices.append(DeviceResponse(
            id=device.id,
            imei=device.imei,
            nickname=user_device.nickname,
            relation=user_device.relation,
            iccid=device.iccid,
            firmware_version=device.firmware_version,
            hardware_version=device.hardware_version,
            battery=device.battery,
            signal_strength=device.signal_strength,
            mode=device.mode,
            status=device.status,
            last_location_lat=device.last_location_lat,
            last_location_lng=device.last_location_lng,
            last_location_time=device.last_location_time.isoformat() if device.last_location_time else None,
            created_at=device.created_at.isoformat() if device.created_at else None,
        ))

    return DeviceListResponse(devices=devices, total=len(devices))


@router.get("/{device_imei}", response_model=DeviceResponse)
async def get_device(
    device_imei: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取指定设备详情"""
    user_id = current_user.id

    if demo_data_service.is_demo_user(user_id):
        demo_devices = demo_data_service.get_demo_devices()
        for d in demo_devices:
            if d["imei"] == device_imei:
                return DeviceResponse(**d)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )

    # 查询设备并验证归属
    result = await db.execute(
        select(UserDevice, Device)
        .join(Device, UserDevice.device_id == Device.id)
        .where(
            Device.imei == device_imei,
            UserDevice.user_id == user_id,
            UserDevice.status == "active"
        )
    )
    row = result.scalar_one_or_none()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在或无权访问"
        )

    user_device, device = row

    return DeviceResponse(
        id=device.id,
        imei=device.imei,
        nickname=user_device.nickname,
        relation=user_device.relation,
        iccid=device.iccid,
        firmware_version=device.firmware_version,
        hardware_version=device.hardware_version,
        battery=device.battery,
        signal_strength=device.signal_strength,
        mode=device.mode,
        status=device.status,
        last_location_lat=device.last_location_lat,
        last_location_lng=device.last_location_lng,
        last_location_time=device.last_location_time.isoformat() if device.last_location_time else None,
        created_at=device.created_at.isoformat() if device.created_at else None,
    )


@router.delete("/{device_imei}/unbind")
async def unbind_device(
    device_imei: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """解除设备绑定"""
    user_id = current_user.id

    # 查询并验证归属
    result = await db.execute(
        select(UserDevice, Device)
        .join(Device, UserDevice.device_id == Device.id)
        .where(
            Device.imei == device_imei,
            UserDevice.user_id == user_id,
            UserDevice.status == "active"
        )
    )
    row = result.scalar_one_or_none()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在或无权访问"
        )

    user_device, _ = row

    # 软删除绑定关系
    user_device.status = "unbinded"
    await db.commit()

    return {"message": "解除绑定成功"}
