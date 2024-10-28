import importlib
import os
import platform
import re
from pathlib import Path

import bpy
from bpy.app.handlers import persistent

from . import __package__ as base_package

ADDON_ID = base_package


def addon_name():
    return "WXZ Pie Menus Addon"


def get_prefs():
    return bpy.context.preferences.addons[ADDON_ID].preferences


def is_windows():
    return platform.system() == "Windows"


def is_macos():
    return platform.system() == "Darwin"


def get_sync_path():
    if is_windows():
        return "D:/BaiduSyncdisk/Blender Assets"
    if is_macos():
        return "/Users/wangxianzhi/Library/CloudStorage/OneDrive-个人/Sync/Blender/Assets Sync"


def get_local_path():
    if is_windows():
        return "F:/Blender Assets"
    if is_macos():
        return "/Users/wangxianzhi/Blender Lib"


def get_desktop_path():
    """获取win桌面路径,即使路径被手动更改了(从注册表获取)"""
    if is_windows():
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        ) as key:
            desktop_path, _ = winreg.QueryValueEx(key, "Desktop")
            return desktop_path
    elif is_macos():
        return os.path.join(os.path.expanduser("~"), "Desktop")


def prefs_show_sub_panel(self, layout, show_prop):
    attr = getattr(self, show_prop)
    col = layout.box().column()
    col.scale_y = 1.1
    col.use_property_split = False
    col.prop(self, show_prop, icon="TRIA_RIGHT" if attr else "TRIA_DOWN")
    return (attr, col)


@persistent
def manage_app_handlers(handler_list, func, remove=False):
    for handler in handler_list:
        handls = getattr(bpy.app.handlers, handler)
        if remove:
            if func in handls:
                handls.remove(func)
        else:
            if func not in handls:
                handls.append(func)


def iter_submodules_name(path, except_package_list):
    path = Path(path)
    name_list = []

    for entry in path.iterdir():
        if entry.is_dir():
            dir_name = entry.name
            if dir_name not in except_package_list:
                name_list.append(dir_name)
        elif entry.is_file():
            file_name = entry.stem
            file_suffix = entry.suffix
            if file_name not in except_package_list and file_suffix != ".json":
                name_list.append(file_name)

    path_base_name = path.name.split(".")[0]
    sub_modules = []

    for submod in name_list:
        if not submod.startswith("."):
            full_module_name = f"{__package__}.{path_base_name}.{submod}"
            sub_modules.append(importlib.import_module(full_module_name))

    sub_modules.sort(key=lambda mod: mod.__name__)
    return sub_modules


def glb_classes_register(CLASSES):
    filename = os.path.splitext(os.path.basename(__file__))[0]
    safe_filename = re.sub(r"\W|^(?=\d)", "_", filename)

    class_register_var_name = f"{safe_filename}_class_register"
    class_unregister_var_name = f"{safe_filename}_class_unregister"

    globals()[class_register_var_name], globals()[class_unregister_var_name] = bpy.utils.register_classes_factory(
        CLASSES
    )

    return (globals()[class_register_var_name], globals()[class_unregister_var_name])


def full_justify(line, max_width):
    """对单行文本进行两端对齐"""
    words = line.split()
    if not words:
        return ""  # 空行直接返回
    if len(words) == 1:
        # 只有一个单词，左对齐
        return words[0].ljust(max_width)
    total_chars = sum(len(word) for word in words)
    total_spaces = max_width - total_chars
    spaces_between_words = len(words) - 1
    min_spaces, extra_spaces = divmod(total_spaces, spaces_between_words)
    # 构建对齐后的行
    justified_line = ""
    for i, word in enumerate(words):
        justified_line += word
        if i < spaces_between_words:
            # 添加最小空格数
            justified_line += " " * (min_spaces + (1 if i < extra_spaces else 0))
    return justified_line
