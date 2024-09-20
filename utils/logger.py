import logging
import os

class SendLogFilter(logging.Filter):
    """自定义过滤器，只允许发送数据的日志通过"""
    def filter(self, record):
        return "接收" in record.getMessage()

class Logger:
    @staticmethod
    def setup_logger():
        """设置日志格式、日志级别和输出文件"""
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=os.path.join(log_dir, 'app.log'),
            filemode='a'
        )

        # 添加自定义过滤器，仅记录发送数据的日志
        file_handler = logging.FileHandler(os.path.join(log_dir, 'send_data.log'), mode='a')
        file_handler.setLevel(logging.INFO)
        file_handler.addFilter(SendLogFilter())
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logging.getLogger().addHandler(file_handler)

    @staticmethod
    def debug(message):
        logging.debug(message)

    @staticmethod
    def info(message):
        logging.info(message)

    @staticmethod
    def warning(message):
        logging.warning(message)

    @staticmethod
    def error(message):
        logging.error(message)

    @staticmethod
    def critical(message):
        logging.critical(message)
