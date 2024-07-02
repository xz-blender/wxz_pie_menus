import os

import bpy
from bpy.types import Menu, Operator

from .utils import *

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


class PIE_OP_A_alt_shift(Operator):
    bl_idname = "pie.alt_shift_a_key"
    bl_label = "折叠所有修改器面板"

    @classmethod
    def poll(cls, context):
        return context.selectable_objects is not None

    def execute(self, context):
        if context.area.ui_type == "PROPERTIES":
            try:
                bpy.ops.wm.toggle_all_show_expanded()
            except:
                self.report({"ERROR"}, "未开启ModifierTools插件!")
        return {"FINISHED"}


classes = [PIE_OP_A_alt_shift]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="Window", space_type="EMPTY")
    kmi = km.keymap_items.new(PIE_OP_A_alt_shift.bl_idname, "A", "PRESS", shift=True, alt=True)
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
        try:
            bpy.utils.register_class(cls)
        except:
            pass
    register_keymaps()


def unregister():
    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
