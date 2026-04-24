# -*- coding: utf-8 -*-
"""
HTTP API应用入口
足安智能防走失系统 Web API服务
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logger import logger
from app.core.database.session import init_all_databases, close_all_databases


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Starting HTTP API server...")
    await init_all_databases()
    logger.info("Databases initialized")

    yield

    # 关闭时
    logger.info("Shutting down HTTP API server...")
    await close_all_databases()
    logger.info("HTTP API server stopped")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="足安智能防走失系统 API",
        description="足安智能防走失系统 Web端和移动端API接口",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    from app.api.routes import auth, devices, alarms, locations, fences, contacts

    app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
    app.include_router(devices.router, prefix="/api/devices", tags=["设备"])
    app.include_router(alarms.router, prefix="/api/alarms", tags=["报警"])
    app.include_router(locations.router, prefix="/api/locations", tags=["位置"])
    app.include_router(fences.router, prefix="/api/fences", tags=["电子围栏"])
    app.include_router(contacts.router, prefix="/api/contacts", tags=["联系人"])

    @app.get("/api/health")
    async def health_check():
        """健康检查"""
        return {"status": "ok", "service": "足安智能防走失系统 API"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
