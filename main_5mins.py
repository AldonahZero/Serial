from venv import logger

import serial
import serial.tools.list_ports
import threading
import platform
import time
from utils.logger import Logger  # 引入刚刚创建的日志工具类

class SerialDebugger:
    def __init__(self):
        self.serial_port = None
        self.is_running = False
        self.timer_started = False
        Logger.setup_logger()

    def list_ports(self):
        """列出可用的串口，返回端口列表"""
        ports = serial.tools.list_ports.comports()
        if not ports:
            print("未找到可用的串口设备。")
        else:
            for port in ports:
                print(f"{port.device}: {port.description}")
        return [port.device for port in ports]

    def get_min_port(self, ports):
        """获取编号最小的串口"""
        if platform.system() == "Windows":
            sorted_ports = sorted(ports, key=lambda x: int(x[3:]))
        else:
            sorted_ports = sorted(ports, key=lambda x: int(''.join(filter(str.isdigit, x))))
        return sorted_ports[0] if sorted_ports else None

    def open_port(self, port_name, baudrate=9600):
        """尝试打开串口"""
        try:
            self.serial_port = serial.Serial(port_name, baudrate, timeout=1)
            self.is_running = True
            print(f"已打开端口 {port_name}，波特率为 {baudrate}。")
            threading.Thread(target=self.read_from_port).start()
        except Exception as e:
            print(f"打开串口失败: {e}")

    def close_ports(self):
        """关闭串口"""
        if self.serial_port and self.serial_port.is_open:
            self.is_running = False
            self.serial_port.close()
            print("已关闭串口。")

    def read_from_port(self):
        """从串口读取数据并处理"""
        buffer = bytearray()
        while self.is_running:
            if self.serial_port.in_waiting > 0:
                try:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    buffer.extend(data)

                    # 记录接收到的数据并启动倒计时
                    if not self.timer_started:
                        self.timer_started = True
                        threading.Thread(target=self.start_timer).start()

                    hex_data = ' '.join(f'{byte:02X}' for byte in data)
                    logger.info(f"接收 : {hex_data}")
                    print(f"接收 (HEX): {hex_data}")  # 控制台输出
                except Exception as e:
                    print(f"读取串口数据时出错: {e}")

    def start_timer(self):
        """启动五分钟倒计时"""
        countdown = 5 * 60  # 5分钟
        while countdown > 0 and self.is_running:
            time.sleep(1)
            countdown -= 1
        if self.is_running:
            print("倒计时结束，程序将停止。")
            self.close_ports()

    def start(self):
        """启动串口监控"""
        available_ports = self.list_ports()
        if not available_ports:
            print("未发现可用的串口。")
            return

        min_port = self.get_min_port(available_ports)
        if min_port:
            print(f"最小编号的串口是: {min_port}")
        else:
            print("未找到可用的串口。")
            return

        port_name = input(f"请输入要打开的端口（按回车默认打开最小编号的端口 {min_port}）：")
        if not port_name:
            port_name = min_port

        baudrate = int(input("请输入波特率（默认 9600）：") or 9600)
        self.open_port(port_name, baudrate)

        input("按回车键退出。")  # 保持程序运行，直到用户按下回车
        self.close_ports()

if __name__ == "__main__":
    debugger = SerialDebugger()
    debugger.start()
