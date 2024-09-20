import serial
import serial.tools.list_ports
import threading
import platform
import time
import logging
import os

class Logger:
    @staticmethod
    def setup_logger():
        """设置日志格式、日志级别和输出文件"""
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=os.path.join(log_dir, 'received_data.log'),
            filemode='a'
        )

class ScanSerialDebugger:
    def __init__(self):
        self.serial_port = None
        self.is_running = False
        Logger.setup_logger()

    def list_ports(self):
        """列出可用的串口，返回端口列表"""
        ports = serial.tools.list_ports.comports()
        if not ports:
            logging.warning("未找到可用的串口设备。")
        else:
            for port in ports:
                logging.info(f"{port.device}: {port.description}")
        return [port.device for port in ports]

    def open_port(self, port_name, baudrate=9600):
        """尝试打开串口"""
        try:
            self.serial_port = serial.Serial(port_name, baudrate, timeout=1)
            self.is_running = True
            logging.info(f"已打开端口 {port_name}，波特率为 {baudrate}。")
            return True
        except Exception as e:
            logging.error(f"打开串口 {port_name} 失败: {e}")
            return False

    def read_from_port(self):
        """从串口读取数据并记录到文件"""
        buffer = bytearray()
        start_time = time.time()
        while self.is_running and (time.time() - start_time < 10):
            if self.serial_port.in_waiting > 0:
                try:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    buffer.extend(data)
                    logging.info(f"接收 (HEX): {' '.join(f'{byte:02X}' for byte in data)}")
                    return  # 一旦接收到数据，退出读取
                except Exception as e:
                    logging.error(f"读取串口数据时出错: {e}")

    def start(self):
        """启动串口轮询"""
        available_ports = self.list_ports()
        if not available_ports:
            logging.warning("未发现可用的串口。")
            return

        for port_name in available_ports:
            if self.open_port(port_name):
                self.read_from_port()
                self.close_port()

    def close_port(self):
        """关闭当前打开的串口"""
        if self.serial_port and self.serial_port.is_open:
            self.is_running = False
            self.serial_port.close()
            logging.info("已关闭串口。")

if __name__ == "__main__":
    debugger = ScanSerialDebugger()
    debugger.start()
