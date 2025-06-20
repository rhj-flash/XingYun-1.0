import os
import sys
import time
import subprocess

print("正在启动程序...")
try:
    os.chdir(r"D:\python\pythonProject2")  # 切换到项目目录
    result = subprocess.run(['python', 'window.py'], capture_output=True, text=True, check=True)
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print(f"程序运行出错：{e.stderr}")
    print("请检查是否已安装所有必需的包")
    input("按回车键退出...")