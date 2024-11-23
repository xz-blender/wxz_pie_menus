import importlib
import inspect
import os
import platform
import re
from pathlib import Path

import bpy
from bpy.app.handlers import persistent
from bpy.types import PointerProperty, PropertyGroup
from mathutils import Euler, Matrix, Vector

from . import __package__ as ADDON_ID
from .items import All_Pie_keymaps, ignore_op_props


def addon_name():
    return "WXZ Pie Menus Addon"


def get_prefs():
    addon = bpy.context.preferences.addons.get(ADDON_ID)
    if addon and addon.preferences:
        return addon.preferences
    else:
        print(f"插件 '{ADDON_ID}' 未加载或启用，或没有偏好设置。")
        return None


def is_windows():
    return platform.system() == "Windows"


def is_macos():
    return platform.system() == "Darwin"


def get_config_path():
    return bpy.utils.user_resource("CONFIG")


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


def prefs_show_sub_panel(self, layout, show_prop, prop_name=""):
    if not show_prop in self.keys():
        # 如果属性不存在，使用 ID 属性（自定义属性）来存储
        self[show_prop] = False  # 设置默认值为 False
    attr = self[show_prop]
    # 创建 UI 布局
    col = layout.box().column()
    col.scale_y = 1.1
    col.use_property_split = False
    name: str = prop_name if prop_name != "" else show_prop
    # 旧方法 col.prop(self, show_prop, icon="")
    # 新方法 使用 ID 属性的语法访问属性
    col.prop(self, f'["{show_prop}"]', text=name, icon="TRIA_DOWN" if attr else "TRIA_RIGHT")

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


def safe_register_class(classes):
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
        bpy.utils.register_class(cls)


def safe_unregister_class(classes):
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass


def extend_keymaps_list(keymaps: list):
    All_Pie_keymaps.extend(keymaps)


def get_kmi_operator_properties(kmi: "bpy.types.KeyMapItem") -> dict:
    """获取kmi操作符的属性"""
    properties = kmi.properties
    prop_keys = dict(properties.items()).keys()
    dictionary = {i: getattr(properties, i, None) for i in prop_keys}
    del_key = []
    for item in dictionary:
        prop = getattr(properties, item, None)
        typ = type(prop)
        if prop:
            if typ == Vector:
                # 属性阵列-浮点数组
                dictionary[item] = dictionary[item].to_tuple()
            elif typ == Euler:
                dictionary[item] = dictionary[item][:]
            elif typ == Matrix:
                dictionary[item] = tuple(i[:] for i in dictionary[item])
            elif typ == bpy.types.bpy_prop_array:
                dictionary[item] = dictionary[item][:]
            elif typ in (str, bool, float, int, set, list, tuple):
                pass
            elif typ.__name__ in ignore_op_props:  # 一些奇怪的操作符属性,不太好解析也用不上
                del_key.append(item)
            else:
                print("emm 未知属性,", typ, dictionary[item])
                # del_key.append(item)
    for i in del_key:
        dictionary.pop(i)
    return dictionary
