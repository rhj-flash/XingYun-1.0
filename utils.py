import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

def get_resource_path(relative_path):
    """
    获取资源的绝对路径，兼容PyInstaller打包。
    当程序被打包成exe时，资源文件会被放在一个临时目录，sys._MEIPASS指向该目录。
    当程序作为脚本运行时，则使用当前文件所在的目录作为基准。

    Args:
        relative_path (str): 资源的相对路径。

    Returns:
        str: 资源的绝对路径。
    """
    try:
        # PyInstaller 打包后的临时目录
        base_path = sys._MEIPASS
    except AttributeError:
        # 脚本运行时的文件目录
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

# --- 缓存相关变量和对象 ---

# 创建一个缓存目录，确保它存在
ICON_CACHE_DIR = get_resource_path('resources/icon_cache')
os.makedirs(ICON_CACHE_DIR, exist_ok=True)

# 缓存锁，用于多线程环境下安全访问缓存
CACHE_LOCK = threading.Lock()

# 图标缓存字典，用于存储已加载的图标
ICON_CACHE = {}

# 线程池执行器，用于异步任务
ICON_EXECUTOR = ThreadPoolExecutor(max_workers=32)

# --- 其他可能需要的通用工具函数 ---
# 可以在此文件中添加其他通用工具函数，以便集中管理