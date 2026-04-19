# 足安智能防走失系统
# 多阶段构建Dockerfile

# ==================== 阶段1：构建阶段 ====================
FROM python:3.11-slim as builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --user -r requirements.txt

# ==================== 阶段2：运行阶段 ====================
FROM python:3.11-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi8 \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制已安装的包
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 复制应用代码
COPY app/ ./app/

# 创建日志目录
RUN mkdir -p /var/log/terminal_service

# 创建非root用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /var/log/terminal_service

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 8888/udp 8889/tcp

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; socket.socket(socket.AF_INET, socket.SOCK_DGRAM).connect(('127.0.0.1', 8888))"

# 启动命令
CMD ["python", "-m", "app.main"]
