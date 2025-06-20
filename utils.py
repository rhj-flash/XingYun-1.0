import os
import sys
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor

def get_resource_path(relative_path):
    """获取资源文件路径（开发/打包环境兼容）
    同时支持单词表、主图标和缓存图标
    """
    is_frozen = getattr(sys, 'frozen', False)

    # 处理图标缓存路径
    if relative_path.startswith("icon_cache/"):
        if is_frozen:
            # 打包环境 - 使用用户目录
            base_dir = os.path.join(os.path.expanduser("~"), "Xingyun")
        else:
            # 开发环境 - 使用项目目录
            base_dir = os.path.dirname(os.path.abspath(__file__))

        cache_dir = os.path.join(base_dir, "icon_cache")
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, relative_path[11:])

    # 处理其他资源路径
    if is_frozen:
        # 打包环境优先使用临时解压目录
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        # 开发环境使用项目目录
        base_path = os.path.dirname(os.path.abspath(__file__))

    # 标准化资源路径
    if relative_path.startswith("resources/"):
        relative_path = relative_path[9:]

    full_path = os.path.join(base_path, "resources", relative_path)

    # 后备检查：如果文件不存在，尝试用户目录
    if not os.path.exists(full_path) and is_frozen:
        user_dir = os.path.join(os.path.expanduser("~"), "Xingyun")
        user_path = os.path.join(user_dir, "resources", relative_path)
        if os.path.exists(user_path):
            return user_path

    return full_path

# 用于线程安全的锁
CACHE_LOCK = threading.Lock()
# 图标缓存
ICON_CACHE = {}
# 线程池
ICON_EXECUTOR = ThreadPoolExecutor(max_workers=50)
