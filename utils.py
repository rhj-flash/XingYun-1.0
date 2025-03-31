import os
import sys
import shutil

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        resources_dir = os.path.join(base_path, "resources")
        if not os.path.exists(resources_dir):
            original_resources = os.path.join(sys._MEIPASS, "resources")
            shutil.copytree(original_resources, resources_dir)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
