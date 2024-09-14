import serial
import serial.tools.list_ports
import threading
import platform

class SerialDebugger:
    def __init__(self):
        # 初始化串口调试助手
        self.serial_port = None
        self.is_running = False

    def list_ports(self):
        """列出可用的串口"""
        ports = serial.tools.list_ports.comports()
        if not ports:
            print("未找到可用的串口设备。")
        else:
            print("可用串口:")
            for port in ports:
                print(f"{port.device}: {port.description}")
        return [port.device for port in ports]

    def open_port(self, port_name, baudrate=9600):
        """打开串口"""
        try:
            self.serial_port = serial.Serial(port_name, baudrate, timeout=1)
            self.is_running = True
            print(f"已打开端口 {port_name}，波特率为 {baudrate}。")
            # 开启一个新线程来监听串口数据
            threading.Thread(target=self.read_from_port).start()
        except Exception as e:
            print(f"打开串口失败: {e}")

    def close_port(self):
        """关闭串口"""
        if self.serial_port and self.serial_port.is_open:
            self.is_running = False
            self.serial_port.close()
            print("已关闭串口。")

    def send_data(self, data):
        """发送数据到串口"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(data.encode())
            print(f"发送: {data}")
        else:
            print("串口未打开，无法发送数据。")

    def read_from_port(self):
        """从串口读取数据"""
        while self.is_running:
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.readline().decode('utf-8').strip()
                if data:
                    print(f"接收: {data}")

    def get_default_port_format(self):
        """根据操作系统返回默认串口格式"""
        os_system = platform.system()
        if os_system == "Windows":
            return "COMx (例如 COM3)"
        elif os_system == "Darwin":  # Mac OS
            return "/dev/tty.usbserial (例如 /dev/tty.usbserial-0001)"
        elif os_system == "Linux":
            return "/dev/ttyUSBx (例如 /dev/ttyUSB0)"
        else:
            return "未知系统，无法提供默认串口格式"

    def start(self):
        """启动串口调试助手"""
        # 列出所有可用的串口
        available_ports = self.list_ports()
        if not available_ports:
            print("未发现可用的串口。")
            return

        # 获取平台相关的串口格式提示
        default_port_format = self.get_default_port_format()
        print(f"您的系统是 {platform.system()}，默认的串口格式为: {default_port_format}")

        # 选择要打开的串口和波特率
        port_name = input(f"请输入要打开的端口（例如 {default_port_format}）：")
        baudrate = int(input("请输入波特率（默认 9600）：") or 9600)

        # 打开指定的串口
        self.open_port(port_name, baudrate)

        # 循环等待用户输入要发送的数据
        while True:
            cmd = input("请输入要发送的数据（输入 'exit' 退出）：")
            if cmd.lower() == 'exit':
                self.close_port()
                break
            else:
                self.send_data(cmd)


if __name__ == "__main__":
    # 实例化并启动串口调试助手
    debugger = SerialDebugger()
    debugger.start()
