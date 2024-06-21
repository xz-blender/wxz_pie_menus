import platform
from pathlib import Path

import bpy


def get_sync_path():
    if platform.system() == "Windows":
        return r"D:/BaiduSyncdisk/Blender Assets"
    elif platform.system() == "Darwin":
        return r"/Users/wangxianzhi/Library/CloudStorage/OneDrive-个人/Sync/Blender/Assets Sync"


def get_local_path():
    if platform.system() == "Windows":
        return r"F:/Blender Assets"
    elif platform.system() == "Darwin":
        return r"/Users/wangxianzhi/Blender Lib"


def get_addon_name():
    if bpy.app.version < (4, 2, 0):
        return Path(__file__).parent.name
    else:
        return __package__
