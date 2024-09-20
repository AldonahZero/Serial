import serial
import serial.tools.list_ports
import threading
import platform
from utils.logger import Logger  # 引入刚刚创建的日志工具类

class SerialDebugger:
    def __init__(self):
        self.serial_port = None
        self.is_running = False
        Logger.setup_logger()

    def list_ports(self):
        ports = serial.tools.list_ports.comports()
        if not ports:
            Logger.warning("未找到可用的串口设备。")
        else:
            for port in ports:
                Logger.info(f"{port.device}: {port.description}")
        return [port.device for port in ports]

    def get_min_port(self, ports):
        if platform.system() == "Windows":
            sorted_ports = sorted(ports, key=lambda x: int(x[3:]))
        else:
            sorted_ports = sorted(ports, key=lambda x: int(''.join(filter(str.isdigit, x))))
        return sorted_ports[0] if sorted_ports else None

    def open_port(self, port_name, baudrate=9600):
        try:
            self.serial_port = serial.Serial(port_name, baudrate, timeout=1)
            self.is_running = True
            Logger.info(f"已打开端口 {port_name}，波特率为 {baudrate}。")
            threading.Thread(target=self.read_from_port).start()
        except Exception as e:
            Logger.error(f"打开串口失败: {e}")

    def close_ports(self):
        if self.serial_port and self.serial_port.is_open:
            self.is_running = False
            self.serial_port.close()
            Logger.info("已关闭串口。")

    def read_from_port(self):
        buffer = bytearray()
        while self.is_running:
            if self.serial_port.in_waiting > 0:
                try:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    buffer.extend(data)

                    while len(buffer) >= 8:
                        hex_data = ' '.join(f'{byte:02X}' for byte in buffer[:8])
                        Logger.info(f"接收 (HEX): {hex_data}")
                        buffer = buffer[8:]
                except Exception as e:
                    Logger.error(f"读取串口数据时出错: {e}")

    def start(self):
        available_ports = self.list_ports()
        if not available_ports:
            Logger.warning("未发现可用的串口。")
            return

        min_port = self.get_min_port(available_ports)
        if min_port:
            Logger.info(f"最小编号的串口是: {min_port}")
        else:
            Logger.warning("未找到可用的串口。")
            return

        port_name = input(f"请输入要打开的端口（按回车默认打开最小编号的端口 {min_port}）：")
        if not port_name:
            port_name = min_port

        baudrate = int(input("请输入波特率（默认 9600）：") or 9600)
        self.open_port(port_name, baudrate)

        input("按回车键退出。")
        self.close_ports()

if __name__ == "__main__":
    debugger = SerialDebugger()
    debugger.start()
