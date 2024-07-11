import os
import platform
from pathlib import Path

import bpy


def get_prefs():
    return bpy.context.preferences.addons[__package__].preferences


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


def get_desktop_path():
    """获取win桌面路径，即使路径被手动更改了(从注册表获取)"""
    import winreg

    # Open the registry key
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
    ) as key:
        # Query the value for the Desktop
        desktop_path, _ = winreg.QueryValueEx(key, "Desktop")
        return desktop_path


def iter_submodules_name(path, except_package_list):
    name_list = []
    for entry in os.listdir(path):
        entry_path = os.path.join(path, entry)
        if os.path.isdir(entry_path):
            dir_name = os.path.basename(entry_path)
            if dir_name not in except_package_list:
                name_list.append(dir_name)
        elif os.path.isfile(entry_path):
            file_name = os.path.splitext(entry)[0]
            if file_name not in except_package_list:
                name_list.append(file_name)
    path_base_name = os.path.basename(path).split(".")[0]
    sub_modules = []
    for submod in name_list:
        if not submod.startswith("."):
            sub_modules.append(__import__(__package__ + "." + path_base_name + "." + submod, {}, {}, submod))
    name_list.clear()
    sub_modules.sort(key=lambda mod: (mod.__name__))
    return sub_modules
