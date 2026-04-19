# -*- coding: utf-8 -*-
"""
报警路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database.session import get_db
from app.api.routes.auth import get_current_user
from app.models.orm.device import Device, Alarm
from app.models.orm.user_device import UserDevice
from app.services.demo_data_service import demo_data_service

router = APIRouter()


class AlarmResponse(BaseModel):
    """报警响应"""
    id: int
    alarm_id: str
    device_id: str
    alarm_type: int
    alarm_level: int
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    accuracy: Optional[str] = None
    battery: Optional[int] = None
    status: str
    alarm_data: Optional[str] = None
    created_at: Optional[str] = None


class AlarmListResponse(BaseModel):
    """报警列表响应"""
    alarms: List[AlarmResponse]
    total: int


@router.get("/", response_model=AlarmListResponse)
async def get_alarms(
    device_imei: Optional[str] = Query(None, description="设备IMEI"),
    alarm_type: Optional[int] = Query(None, description="报警类型"),
    status: Optional[str] = Query(None, description="状态"),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取报警列表（只返回用户绑定设备的报警）"""
    user_id = current_user.id

    if demo_data_service.is_demo_user(user_id):
        demo_alarms = demo_data_service.get_demo_alarms()
        filtered_alarms = demo_alarms
        if device_imei:
            filtered_alarms = [a for a in filtered_alarms if a["device_id"] == device_imei]
        if alarm_type is not None:
            filtered_alarms = [a for a in filtered_alarms if a["alarm_type"] == alarm_type]
        if status:
            filtered_alarms = [a for a in filtered_alarms if a["status"] == status]
        paginated_alarms = filtered_alarms[offset:offset + limit]
        return AlarmListResponse(
            alarms=[AlarmResponse(**a) for a in paginated_alarms],
            total=len(filtered_alarms)
        )

    # 获取用户的所有设备ID
    result = await db.execute(
        select(Device.id)
        .join(UserDevice, UserDevice.device_id == Device.id)
        .where(UserDevice.user_id == user_id, UserDevice.status == "active")
    )
    device_ids = [row[0] for row in result.all()]

    if not device_ids:
        return AlarmListResponse(alarms=[], total=0)

    # 构建查询
    query = select(Alarm).where(Alarm.device_id.in_([str(d) for d in device_ids]))

    if device_imei:
        # 需要先找到设备ID
        device_result = await db.execute(select(Device.id).where(Device.imei == device_imei))
        device_id = device_result.scalar_one_or_none()
        if device_id:
            query = query.where(Alarm.device_id == str(device_id))

    if alarm_type is not None:
        query = query.where(Alarm.alarm_type == alarm_type)

    if status:
        query = query.where(Alarm.status == status)

    # 统计总数
    count_result = await db.execute(
        select(Alarm).where(Alarm.device_id.in_([str(d) for d in device_ids]))
    )
    total = len(count_result.scalars().all())

    # 分页查询
    query = query.order_by(desc(Alarm.created_at)).limit(limit).offset(offset)
    result = await db.execute(query)
    alarms = result.scalars().all()

    return AlarmListResponse(
        alarms=[
            AlarmResponse(
                id=alarm.id,
                alarm_id=alarm.alarm_id,
                device_id=alarm.device_id,
                alarm_type=alarm.alarm_type,
                alarm_level=alarm.alarm_level,
                latitude=alarm.latitude,
                longitude=alarm.longitude,
                accuracy=alarm.accuracy,
                battery=alarm.battery,
                status=alarm.status,
                alarm_data=alarm.alarm_data,
                created_at=alarm.created_at.isoformat() if alarm.created_at else None,
            )
            for alarm in alarms
        ],
        total=total
    )


@router.get("/{alarm_id}", response_model=AlarmResponse)
async def get_alarm(
    alarm_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取报警详情"""
    user_id = current_user.id

    # 查询报警
    result = await db.execute(select(Alarm).where(Alarm.alarm_id == alarm_id))
    alarm = result.scalar_one_or_none()

    if alarm is None:
        raise HTTPException(status_code=404, detail="报警不存在")

    # 验证设备归属
    device_result = await db.execute(
        select(Device.id)
        .join(UserDevice, UserDevice.device_id == Device.id)
        .where(
            Device.imei == alarm.device_id,
            UserDevice.user_id == user_id,
            UserDevice.status == "active"
        )
    )
    if device_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=403, detail="无权访问此报警")

    return AlarmResponse(
        id=alarm.id,
        alarm_id=alarm.alarm_id,
        device_id=alarm.device_id,
        alarm_type=alarm.alarm_type,
        alarm_level=alarm.alarm_level,
        latitude=alarm.latitude,
        longitude=alarm.longitude,
        accuracy=alarm.accuracy,
        battery=alarm.battery,
        status=alarm.status,
        alarm_data=alarm.alarm_data,
        created_at=alarm.created_at.isoformat() if alarm.created_at else None,
    )


@router.put("/{alarm_id}/handle")
async def handle_alarm(
    alarm_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """处理报警"""
    user_id = current_user.id

    # 查询报警
    result = await db.execute(select(Alarm).where(Alarm.alarm_id == alarm_id))
    alarm = result.scalar_one_or_none()

    if alarm is None:
        raise HTTPException(status_code=404, detail="报警不存在")

    # 验证设备归属
    device_result = await db.execute(
        select(Device.id)
        .join(UserDevice, UserDevice.device_id == Device.id)
        .where(
            Device.imei == alarm.device_id,
            UserDevice.user_id == user_id,
            UserDevice.status == "active"
        )
    )
    if device_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=403, detail="无权操作此报警")

    alarm.status = "resolved"
    await db.commit()

    return {"message": "报警已处理"}


@router.put("/{alarm_id}/ignore")
async def ignore_alarm(
    alarm_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """忽略报警"""
    user_id = current_user.id

    result = await db.execute(select(Alarm).where(Alarm.alarm_id == alarm_id))
    alarm = result.scalar_one_or_none()

    if alarm is None:
        raise HTTPException(status_code=404, detail="报警不存在")

    device_result = await db.execute(
        select(Device.id)
        .join(UserDevice, UserDevice.device_id == Device.id)
        .where(
            Device.imei == alarm.device_id,
            UserDevice.user_id == user_id,
            UserDevice.status == "active"
        )
    )
    if device_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=403, detail="无权操作此报警")

    alarm.status = "ignored"
    await db.commit()

    return {"message": "报警已忽略"}
