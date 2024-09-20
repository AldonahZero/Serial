import serial
import serial.tools.list_ports
import threading
import platform
from utils.logger import Logger  # 引入刚刚创建的日志工具类

class SerialDebugger:
    def __init__(self):
        self.serial_port = None
        self.is_running = False
        self.com14_port = None
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

    def open_com14_port(self, baudrate=9600):
        try:
            self.com14_port = serial.Serial("COM14", baudrate, timeout=1)
            Logger.info("已打开COM14端口用于数据发送。")
        except Exception as e:
            Logger.error(f"打开 COM14 端口失败: {e}")

    def close_ports(self):
        if self.serial_port and self.serial_port.is_open:
            self.is_running = False
            self.serial_port.close()
            Logger.info("已关闭串口。")

        if self.com14_port and self.com14_port.is_open:
            self.com14_port.close()
            Logger.info("已关闭 COM14 端口。")

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

    def send_to_com14(self, data):
        if self.com14_port and self.com14_port.is_open:
            try:
                self.com14_port.write(data)
                Logger.info(f"发送到 COM14 的数据: {data.hex(' ')}")
            except Exception as e:
                Logger.error(f"发送数据到 COM14 时出错: {e}")
        else:
            Logger.warning("COM14 未打开，无法发送数据。")

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
                        self.send_to_com14(buffer[:8])
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
        # self.open_com14_port(baudrate)
        #
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