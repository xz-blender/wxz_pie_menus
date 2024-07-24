bl_info = {
    "name": "m4_tools_split",
    "author": "ah",
    "description": "ah",
    "blender": (4, 2, 0),
    "version": (1, 0, 0),
    "location": "3D View",
    "category": "Interface",
}

import bpy
from .align import AlignEditMesh, AlignObjectToEdge, AlignObjectToVert, CenterEditMesh, Straighten
from .align_helper import AlignObject
from .align_helper_npanels import ObjectAlignPanel
from .align_helper_panel import PanelM4A1tools
from .align_helper_uv import AlignUV
from .focus_handler import delay_execution, manage_focus_HUD
from .mirror import Mirror

from pathlib import Path

import bpy.utils.previews

previews_icons = {}

thumbnail_suffix = [".png", ".jpg"]  # 缩略图后缀列表


def get_icon(name="None"):
    """
    load icon
    :param name:
    :return:
    """

    return previews_icons["ah"][name].icon_id


def preload_icons():
    """预加载图标，在启动 Blender 或启用插件时加载图标"""
    global previews_icons
    previews_icons["ah"] = bpy.utils.previews.new()  # 用于存所有的缩略图
    # 获取当前文件的目录路径
    folder_path = Path(__file__).parent / "icons"

    # 遍历目录中的所有文件
    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix in thumbnail_suffix:
            # print("文件名", file_path.stem)
            previews_icons["ah"].load(
                file_path.stem,  # 使用文件名（无后缀）作为键名
                str(file_path),  # 转换为字符串路径以供 `load` 使用
                "IMAGE",
            )


classes = [
    ObjectAlignPanel,
    PanelM4A1tools,
    AlignUV,
    Mirror,
    AlignObject,
    CenterEditMesh,
    AlignObjectToEdge,
    AlignObjectToVert,
    Straighten,
    AlignEditMesh,
]
class_register, class_unregister = bpy.utils.register_classes_factory(classes)
addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new(Mirror.bl_idname, "R", "PRESS", ctrl=True, shift=True, alt=True)

    addon_keymaps.append((km, kmi))


def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register():
    class_register()
    preload_icons()
    delay_execution(manage_focus_HUD)
    # register_keymaps()


def unregister():
    class_unregister()
    # unregister_keymaps()
    global previews_icons
    for pcoll in previews_icons.values():
        # print('对齐',pcoll)
        bpy.utils.previews.remove(pcoll)

    previews_icons.clear()


if __name__ == "__main__":
    register()
