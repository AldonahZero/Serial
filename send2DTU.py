import re

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
        self.COM4_port = None
        self.data_buffer = []
        Logger.setup_logger()

    def list_ports(self):
        ports = serial.tools.list_ports.comports()
        if not ports:
            Logger.warning("未找到可用的串口设备。")
        else:
            for port in ports:
                Logger.info(f"{port.device}: {port.description}")
        return [port.device for port in ports]

    def open_port(self, port_name="COM4", baudrate=9600):
        try:
            self.serial_port = serial.Serial(port_name, baudrate, timeout=1)
            self.is_running = True
            Logger.info(f"已打开端口 {port_name}，波特率为 {baudrate}。")
            threading.Thread(target=self.read_from_port).start()
        except Exception as e:
            Logger.error(f"打开串口失败: {e}")

    def open_COM4_port(self, baudrate=9600):
        try:
            self.COM4_port = serial.Serial("COM4", baudrate, timeout=1)
            Logger.info("已打开COM4端口用于数据发送。")
        except Exception as e:
            Logger.error(f"打开 COM4 端口失败: {e}")

    def close_ports(self):
        if self.serial_port and self.serial_port.is_open:
            self.is_running = False
            self.serial_port.close()
            Logger.info("已关闭串口。")

        if self.COM4_port and self.COM4_port.is_open:
            self.COM4_port.close()
            Logger.info("已关闭 COM4 端口。")

    def send_data(self, data):
        if self.serial_port and self.serial_port.is_open:
            try:
                hex_data = bytes.fromhex(data)
                self.serial_port.write(hex_data)
                Logger.info(f"发送 (HEX): {data}")
            except ValueError:
                Logger.error("无效的HEX格式输入，请确保HEX输入有效。")
        else:
            Logger.warning("串口未打开，无法发送数据。")

        # 发送数据到COM4
        if self.COM4_port and self.COM4_port.is_open:
            try:
                self.COM4_port.write(data.encode())  # 发送数据到COM4端口
                Logger.info(f"已向COM4发送数据: {data}")
            except Exception as e:
                Logger.error(f"发送数据到COM4时出错: {e}")

    def read_from_port(self):
        buffer = bytearray()
        while self.is_running:
            if self.serial_port.in_waiting > 0:
                try:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    buffer.extend(data)

                    while len(buffer) >= 8:
                        hex_data = ' '.join(f'{byte:02X}' for byte in buffer[:8])
                        Logger.info(f"接收 : {hex_data}")
                        self.send_to_COM4(buffer[:8])
                        buffer = buffer[8:]
                except Exception as e:
                    Logger.error(f"读取串口数据时出错: {e}")

    def load_data_from_file(self, filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
            # 移除换行符
            content = content.replace("\n", " ").replace("\r", "")
            # 使用正则表达式来匹配以A9 9A开头，0D 0A结尾的内容
            matches = re.findall(r"(A9 9A.*?0D 0A)", content, re.DOTALL)
            self.data_buffer = matches

    def send_data_from_buffer(self):
        for data in self.data_buffer:
            data = data.replace(" ", "")
            print(data)
            hex_data = bytes.fromhex(data)
            self.send_data(hex_data)
            time.sleep(1)  # 每秒发送一组数据

    def start(self):
        available_ports = self.list_ports()
        if not available_ports:
            Logger.warning("未发现可用的串口。")
            return

        if "COM4" not in available_ports:
            Logger.error("未找到COM4端口，无法启动。")
            return

        # 默认打开COM4端口
        baudrate = int(input("请输入波特率（默认 9600）：") or 9600)
        # self.open_port("COM4", baudrate)
        self.open_COM4_port(baudrate)

        # 加载数据
        data_file_path = "./data/data 01.txt"
        self.load_data_from_file(data_file_path)

        # 开始每秒发送一组数据
        self.send_data_from_buffer()

        while True:
            cmd = input("如果需要发送数据\n请输入要发送的16进制数据（输入 'q' 退出）：\n")
            if cmd.lower() == 'q':
                self.close_ports()
                break
            else:
                self.send_data(cmd)


if __name__ == "__main__":
    debugger = SerialDebugger()
    debugger.start()

