import bpy
from bpy.types import Menu, Operator, Panel

from .pie_utils import *


class VIEW3D_PIE_MT_Bottom_T(Menu):
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
                add_operator(pie, "mesh.looptools_relax", text="松弛")
                # 6 - RIGHT
                add_operator(pie, "mesh.looptools_space", text="平均")
                # 2 - BOTTOM
                add_operator(pie, "mesh.looptools_gstretch", text="拉伸")
                # 8 - TOP
                add_operator(pie, "mesh.looptools_circle", text="圆环")
                # 7 - TOP - LEFT
                pie.separator()
                # 9 - TOP - RIGHT
                pie.separator()
                # 1 - BOTTOM - LEFT
                pie.separator()
                # 3 - BOTTOM - RIGHT
                pie.separator()


classes = [
    VIEW3D_PIE_MT_Bottom_T,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    space_name = [
        "Object Mode",
        "Mesh",
        "Curve",
    ]
    for name in space_name:
        km = addon.keymaps.new(name=name)
        kmi = km.keymap_items.new("wm.call_menu_pie", "T", "CLICK_DRAG")
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_T"
        addon_keymaps.append(km)


def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        # wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_keymaps()


def unregister():
    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
