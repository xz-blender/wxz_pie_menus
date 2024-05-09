import os

import bpy
from bpy.types import Menu, Operator, Panel

from .utils import (
    change_default_keymap,
    check_rely_addon,
    pie_op_check,
    rely_addons,
    restored_default_keymap,
    set_pie_ridius,
)

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


class VIEW3D_PIE_MT_Bottom_T(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()

        ob_type = context.object.type
        ob_mode = context.object.mode

        set_pie_ridius(context, 100)

        # addon1:"LoopTools"
        lt_name, lt_path = rely_addons[2][0], rely_addons[2][1]
        lt_check = check_rely_addon(lt_name, lt_path)

        if ob_mode == "EDIT":
            if ob_type == "MESH":
                # 4 - LEFT
                if pie_op_check(pie, lt_check, lt_name) == True:
                    pie.operator("mesh.looptools_relax", text="松弛")
                # 6 - RIGHT
                if pie_op_check(pie, lt_check, lt_name) == True:
                    pie.operator("mesh.looptools_space", text="平均")
                # 2 - BOTTOM
                pie.separator()
                # 8 - TOP
                if pie_op_check(pie, lt_check, lt_name) == True:
                    pie.operator("mesh.looptools_circle", text="圆环")
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


# if __name__ == "__main__":
#     register()
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_T")
