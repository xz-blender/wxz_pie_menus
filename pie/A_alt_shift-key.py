import bpy
from bpy.types import Menu, Operator

from .pie_utils import *


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
class_register, class_unregister = bpy.utils.register_classes_factory(classes)

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="Window", space_type="EMPTY")
    kmi = km.keymap_items.new(PIE_OP_A_alt_shift.bl_idname, "A", "PRESS", shift=True, alt=True)
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
