import os

# 设置文件路径
logs_folder = "./logs"
data_folder = "./data"
output_filename = "data 01.txt"

# 确保data文件夹存在
os.makedirs(data_folder, exist_ok=True)

# 日志文件名列表
log_files = ["id 001.log", "id 002.log", "id 004.log", "id 008.log", "id 010.log", "id 014.log"]

# 用于存储所有日志内容
all_logs = []

# 依次读取每个日志文件
for log_file in log_files:
    log_path = os.path.join(logs_folder, log_file)
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                # 截取“- 接收 : ”之前的内容
                if "- 接收 :" in line:
                    clean_line = line.split("- 接收 :")[-1].strip()
                    all_logs.append(clean_line)

# 将结果写入到data 01.txt文件中
output_path = os.path.join(data_folder, output_filename)
with open(output_path, "w", encoding="utf-8") as output_file:
    for log in all_logs:
        output_file.write(log + "\n")

# 输出完成提示
output_path
