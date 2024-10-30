import bpy
from bpy.types import Menu, Operator, Panel

from ..utils import safe_register_class, safe_unregister_class
from .utils import *


class VIEW3D_PIE_MT_Bottom_V(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius()

        ob_type = get_ob_type(context)
        ob_mode = get_ob_mode(context)

        if ob_mode == "OBJECT":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            col = pie.split().column()
            col.scale_y = 1.7
            col.operator(
                "pie.paste_clipboard_as_image_plane", text="剪切板 -> 参考图", icon="IMAGE_REFERENCE"
            ).is_ref = True
            col.operator("pie.paste_clipboard_as_image_plane", text="剪切板 -> 平面", icon="MESH_PLANE").is_ref = False
            # 8 - TOP
            pie.separator()
            # 7 - TOP - LEFT
            pie.separator()
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            pie.separator()
            # 3 - BOTTOM - RIGHT

        elif ob_mode == "EDIT":
            if ob_type == "CURVE":
                # 4 - LEFT
                pie.operator("curve.handle_type_set", text="矢量", icon="HANDLE_VECTOR").type = "VECTOR"
                # 6 - RIGHT
                pie.operator("curve.handle_type_set", text="对齐", icon="HANDLE_ALIGNED").type = "ALIGNED"
                # 2 - BOTTOM
                pie.separator()
                # 8 - TOP
                pie.operator(
                    "curve.handle_type_set",
                    text="自由/对齐",
                    icon="HANDLE_AUTOCLAMPED",
                ).type = "TOGGLE_FREE_ALIGN"
                # 7 - TOP - LEFT
                pie.operator("curve.handle_type_set", text="自由", icon="HANDLE_FREE").type = "FREE_ALIGN"
                # 9 - TOP - RIGHT
                pie.operator("curve.handle_type_set", text="自动", icon="HANDLE_AUTO").type = "AUTOMATIC"
                # 1 - BOTTOM - LEFT
                pie.separator()
                # 3 - BOTTOM - RIGHT
                pie.separator()

            elif ob_type == "MESH":
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
    VIEW3D_PIE_MT_Bottom_V,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", "V", "CLICK_DRAG")
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_V"

    kmi = km.keymap_items.new("pie.drop_it", "V", "CLICK")
    addon_keymaps.append(km)


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
