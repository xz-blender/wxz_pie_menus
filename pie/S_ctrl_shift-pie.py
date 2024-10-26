from pathlib import Path

import bpy
from bpy.types import Menu, Operator, Panel

from .pie_utils import *


class VIEW3D_MT_PIE_S_ctrl_Shift(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()
        set_pie_ridius()

        temp_path = [path for path in Path(bpy.app.tempdir).resolve().parents][:-3]
        file_path = bpy.data.filepath

        # 4 - LEFT
        pie.separator()
        # try:
        #     pie.operator("rf.callpanel", text="打开附近文件", icon="FILE_TICK", emboss=True)
        #     if file_path and not any(Path(file_path).resolve().is_relative_to(folder) for folder in temp_path):
        #         pp = Path(str(file_path)).parent
        #         context.preferences.addons["Quick Files"].preferences["blends_path"] = str(pp)
        #         bpy.ops.rf.refreshfiles()
        #     else:
        #         context.preferences.addons["Quick Files"].preferences["blends_path"] = "该文件在缓存文件夹中！"
        # except Exception as e:
        #     print(f"Error: {e}")

        # 6 - RIGHT
        pie.separator()
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.operator("pie.estimate_memory_usage", text="展示场景内存使用量", icon="MEMORY")


classes = [
    VIEW3D_MT_PIE_S_ctrl_Shift,
]
class_register, class_unregister = bpy.utils.register_classes_factory(classes)
addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="Object Mode")
    kmi = km.keymap_items.new("wm.call_menu_pie", "S", "CLICK_DRAG", ctrl=True, shift=True)
    kmi.properties.name = "VIEW3D_MT_PIE_S_ctrl_Shift"
    addon_keymaps.append((km, kmi))


def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register():
    class_register()
    register_keymaps()


def unregister():
    class_unregister()
    # unregister_keymaps()
