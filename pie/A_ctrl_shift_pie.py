import bpy
from bpy.types import Menu, Operator

from ..utils import extend_keymaps_list, safe_register_class, safe_unregister_class
from .utils import *


class PIE_MT_Bottom_A_ctrl_shift(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius()

        # 4 - LEFT
        pie.separator()
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
        pie.separator()


CLASSES = [
    PIE_MT_Bottom_A_ctrl_shift,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", "A", "CLICK_DRAG", ctrl=True, shift=True)
    kmi.properties.name = "PIE_MT_Bottom_A_ctrl_shift"
    addon_keymaps.append((km, kmi))


def register():
    safe_register_class(CLASSES)
    register_keymaps()
    extend_keymaps_list(addon_keymaps)


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
