import bpy
from bpy.types import Menu, Operator

from ..utils import safe_register_class, safe_unregister_class
from .utils import *


class VIEW3D_PIE_MT_XZ_Shift_G(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        ob_type = get_ob_type(context)
        ob_mode = get_ob_mode(context)
        ui = get_area_ui_type(context)

        if ui == "VIEW_3D":
            if ob_mode == "OBJECT":
                # 4 - LEFT
                pie.separator()
                # 6 - RIGHT
                split = pie.split().box().column()
                split.operator_enum("object.select_grouped", "type")
                # 2 - BOTTOM
                # 8 - TOP
                # 7 - TOP - LEFT
                # 9 - TOP - RIGHT
                # 1 - BOTTOM - LEFT
                # 3 - BOTTOM - RIGHT
            elif ob_mode == "EDIT":
                # 4 - LEFT
                pie.separator()
                # 6 - RIGHT
                split = pie.split().box().column()
                split.menu_contents("VIEW3D_MT_edit_mesh_select_similar")
                # 2 - BOTTOM
                # 8 - TOP
                # 7 - TOP - LEFT
                # 9 - TOP - RIGHT
                # 1 - BOTTOM - LEFT
                # 3 - BOTTOM - RIGHT

        elif ui == "UV":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            # 2 - BOTTOM
            # 8 - TOP
            # 7 - TOP - LEFT
            # 9 - TOP - RIGHT
            # 1 - BOTTOM - LEFT
            # 3 - BOTTOM - RIGHT


CLASSES = [
    VIEW3D_PIE_MT_XZ_Shift_G,
]

addon_keymaps = []


def register_keymaps():
    spaces = {
        "3D View": "VIEW_3D",
        "UV Editor": "EMPTY",
    }
    for name, space_type in spaces.items():
        kc = bpy.context.window_manager.keyconfigs.addon
        km = kc.keymaps.new(name=name, space_type=space_type)
        kmi = km.keymap_items.new("wm.call_menu_pie", "G", "CLICK_DRAG", shift=True)
        kmi.properties.name = "VIEW3D_PIE_MT_XZ_Shift_G"
        kmi = km.keymap_items.new("pie.ke_mouse_axis_move", "G", "CLICK", shift=True)

        addon_keymaps.append((km, kmi))


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
