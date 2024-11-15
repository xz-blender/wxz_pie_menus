import bpy
from bpy.types import Menu, Operator, Panel

from ..utils import safe_register_class, safe_unregister_class
from .utils import *


class VIEW3D_PIE_MT_Bottom_U(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()
        set_pie_ridius()

        ob_type = get_ob_type(context)
        ob_mode = get_ob_mode(context)

        if ob_mode == "EDIT":
            if ob_type == "MESH":
                # 4 - LEFT
                pie.separator()
                # 6 - RIGHT
                pie.operator("uv.cube_project", text="块面投影")
                # 2 - BOTTOM
                pie.operator("uv.muv_uvw_box_map").assign_uvmap = True
                # 8 - TOP
                pie.operator("uv.project_from_view", text="视角投影")
                # 7 - TOP - LEFT
                pie.separator()
                # 9 - TOP - RIGHT
                pie.separator()
                # 1 - BOTTOM - LEFT
                pie.separator()
                # 3 - BOTTOM - RIGHT
                pie.separator()


CLASSES = [
    VIEW3D_PIE_MT_Bottom_U,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    space_name = [
        "Mesh",
    ]
    for name in space_name:
        km = addon.keymaps.new(name=name)
        kmi = km.keymap_items.new("wm.call_menu_pie", "U", "CLICK_DRAG")
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_U"
        addon_keymaps.append((km, kmi))


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
