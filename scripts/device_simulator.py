# -*- coding: utf-8 -*-
"""
设备模拟器 - 用于测试足安智能防走失系统服务器
模拟鞋垫硬件与服务器通信
"""
import asyncio
import json
import random
import socket
import struct
import time
import hashlib
from datetime import datetime
from typing import Optional

class DeviceSimulator:
    """设备模拟器"""

    def __init__(self, device_imei: str = "860000000000001"):
        self.device_imei = device_imei
        self.session_id: Optional[str] = None
        self.server_host = "localhost"
        self.udp_port = 8888
        self.tcp_port = 8889
        self.preshared_key = "default_preshared_key_change_me"

        # 设备状态
        self.battery = 85
        self.signal_strength = 75
        self.latitude = 39.1028
        self.longitude = 117.3475
        self.altitude = 50.5
        self.speed = 0.0
        self.direction = 0
        self.mode = "normal"

    def generate_nonce(self) -> str:
        """生成12位随机字符串"""
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=12))

    def generate_timestamp(self) -> str:
        """生成ISO 8601格式时间戳"""
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+08:00")

    def calculate_checksum(self, version: str, device_id: str, timestamp: str,
                          nonce: str, data: dict) -> str:
        """计算MD5校验和"""
        data_str = json.dumps(data, separators=(',', ':'), sort_keys=True)
        message = version + device_id + timestamp + nonce + data_str + self.preshared_key
        return hashlib.md5(message.encode()).hexdigest()

    def create_packet(self, msg_type: str, data: dict) -> dict:
        """创建协议报文"""
        timestamp = self.generate_timestamp()
        nonce = self.generate_nonce()

        packet = {
            "version": "1.0",
            "device_id": self.device_imei,
            "timestamp": timestamp,
            "nonce": nonce,
            "type": msg_type,
            "data": data,
            "checksum": self.calculate_checksum("1.0", self.device_imei, timestamp, nonce, data)
        }

        if self.session_id and msg_type != "auth":
            packet["session_id"] = self.session_id

        return packet

    async def send_udp(self, packet: dict) -> None:
        """发送UDP数据"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            data = json.dumps(packet).encode('utf-8')
            sock.sendto(data, (self.server_host, self.udp_port))
            print(f"[UDP] 发送 {packet['type']} 报文: {json.dumps(packet, indent=2)}")
        finally:
            sock.close()

    async def send_tcp(self, packet: dict) -> dict:
        """发送TCP数据并接收响应"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.server_host, self.tcp_port))
            data = json.dumps(packet).encode('utf-8')
            sock.sendall(struct.pack('>I', len(data)) + data)
            print(f"[TCP] 发送 {packet['type']} 报文: {json.dumps(packet, indent=2)}")

            # 接收响应长度
            response_len_bytes = sock.recv(4)
            response_len = struct.unpack('>I', response_len_bytes)[0]

            # 接收响应数据
            response_data = b''
            while len(response_data) < response_len:
                chunk = sock.recv(response_len - len(response_data))
                if not chunk:
                    break
                response_data += chunk

            response = json.loads(response_data.decode('utf-8'))
            print(f"[TCP] 收到响应: {json.dumps(response, indent=2)}")
            return response
        finally:
            sock.close()

    async def test_auth(self) -> bool:
        """测试设备认证"""
        print("\n" + "="*50)
        print("测试设备认证 (TCP)")
        print("="*50)

        data = {
            "firmware_version": "1.2.3",
            "hardware_version": "1.0",
            "iccid": "89860000000000000001",
            "fingerprint": f"device_fp_{self.device_imei}"
        }

        packet = self.create_packet("auth", data)
        response = await self.send_tcp(packet)

        if response.get("code") == 0:
            self.session_id = response.get("data", {}).get("session_id")
            print(f"[认证成功] session_id: {self.session_id}")
            return True
        else:
            print(f"[认证失败] {response.get('message')}")
            return False

    async def test_location_report(self) -> None:
        """测试位置上报"""
        print("\n" + "-"*50)
        print("测试位置上报 (UDP)")

        # 模拟位置变化
        self.latitude += random.uniform(-0.001, 0.001)
        self.longitude += random.uniform(-0.001, 0.001)
        self.speed = random.uniform(0, 2.0)

        data = {
            "latitude": round(self.latitude, 6),
            "longitude": round(self.longitude, 6),
            "altitude": round(self.altitude + random.uniform(-5, 5), 1),
            "speed": round(self.speed, 2),
            "direction": random.randint(0, 359),
            "accuracy": round(random.uniform(5, 15), 1),
            "satellites": random.randint(6, 12),
            "battery": self.battery,
            "signal_strength": self.signal_strength,
            "charging": False,
            "mode": self.mode,
            "gps_timestamp": self.generate_timestamp()
        }

        packet = self.create_packet("location", data)
        await self.send_udp(packet)

    async def test_heartbeat(self) -> None:
        """测试心跳"""
        print("\n" + "-"*50)
        print("测试心跳 (UDP)")

        data = {
            "battery": self.battery,
            "signal_strength": self.signal_strength,
            "charging": False,
            "temperature": round(random.uniform(20, 35), 1)
        }

        packet = self.create_packet("heartbeat", data)
        await self.send_udp(packet)

    async def test_alarm(self, alarm_type: int = 2) -> None:
        """测试报警"""
        print("\n" + "-"*50)
        print(f"测试报警上报 (UDP) - 类型: {alarm_type}")

        alarm_types = {
            1: "防拆报警",
            2: "摔倒报警",
            3: "静止报警",
            4: "低电量报警",
            5: "SOS报警",
            6: "关机报警"
        }

        alarm_levels = {1: 1, 2: 3, 3: 2, 4: 1, 5: 4, 6: 4}

        print(f"报警类型: {alarm_types.get(alarm_type, '未知')}")

        data = {
            "alarm_type": alarm_type,
            "alarm_level": alarm_levels.get(alarm_type, 1),
            "latitude": round(self.latitude, 6),
            "longitude": round(self.longitude, 6),
            "accuracy": round(random.uniform(5, 15), 1),
            "battery": self.battery,
            "alarm_data": self._get_alarm_data(alarm_type)
        }

        packet = self.create_packet("alarm", data)
        await self.send_udp(packet)

    def _get_alarm_data(self, alarm_type: int) -> dict:
        """获取不同报警类型的附加数据"""
        if alarm_type == 1:
            return {"detect_method": "switch"}
        elif alarm_type == 2:
            return {
                "fall_height": round(random.uniform(0.5, 1.5), 1),
                "impact_force": round(random.uniform(10, 20), 1),
                "duration": round(random.uniform(1, 5), 1)
            }
        elif alarm_type == 3:
            return {"still_duration": random.randint(300, 1800)}
        elif alarm_type == 4:
            return {"battery": random.randint(5, 15)}
        elif alarm_type == 5:
            return {"button_press_duration": round(random.uniform(2, 5), 1)}
        elif alarm_type == 6:
            return {"power_off_reason": 0}
        return {}

    async def test_batch_report(self) -> None:
        """测试批量上报"""
        if not self.session_id:
            print("[批量上报] 需要先进行认证")
            return

        print("\n" + "-"*50)
        print("测试批量上报 (TCP)")

        items = []
        base_time = datetime.utcnow()

        # 生成3条位置数据
        for i in range(3):
            items.append({
                "type": "location",
                "timestamp": (base_time.replace(second=base_time.second - i*60)).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
                "data": {
                    "latitude": round(self.latitude + i*0.001, 6),
                    "longitude": round(self.longitude + i*0.001, 6),
                    "altitude": round(self.altitude, 1),
                    "speed": round(self.speed, 2),
                    "direction": random.randint(0, 359),
                    "accuracy": round(random.uniform(5, 15), 1),
                    "satellites": random.randint(6, 12),
                    "battery": self.battery - i,
                    "signal_strength": self.signal_strength,
                    "charging": False,
                    "mode": self.mode,
                    "gps_timestamp": (base_time.replace(second=base_time.second - i*60)).strftime("%Y-%m-%dT%H:%M:%S+08:00")
                }
            })

        data = {
            "total": len(items),
            "index": 1,
            "items": items
        }

        packet = self.create_packet("batch_report", data)
        await self.send_tcp(packet)

    async def run_full_test(self) -> None:
        """运行完整测试流程"""
        print("\n" + "#"*60)
        print("足安智能防走失系统 - 设备模拟器")
        print(f"设备IMEI: {self.device_imei}")
        print(f"服务器: {self.server_host}:{self.udp_port}/{self.tcp_port}")
        print("#"*60)

        # 1. 设备认证
        if not await self.test_auth():
            print("[错误] 设备认证失败，退出测试")
            return

        # 等待一下
        await asyncio.sleep(1)

        # 2. 发送位置数据
        await self.test_location_report()

        # 等待一下
        await asyncio.sleep(0.5)

        # 3. 发送心跳
        await self.test_heartbeat()

        # 等待一下
        await asyncio.sleep(0.5)

        # 4. 测试摔倒报警
        await self.test_alarm(2)

        # 等待一下
        await asyncio.sleep(0.5)

        # 5. 测试批量上报
        await self.test_batch_report()

        print("\n" + "="*50)
        print("测试完成！")
        print("="*50)


async def main():
    """主函数"""
    import sys

    device_imei = sys.argv[1] if len(sys.argv) > 1 else "860000000000001"
    simulator = DeviceSimulator(device_imei)

    try:
        await simulator.run_full_test()
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试出错: {e}")


if __name__ == "__main__":
    asyncio.run(main())
