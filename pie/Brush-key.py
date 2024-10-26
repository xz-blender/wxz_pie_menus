import bpy
from bpy.types import Menu, Operator, Panel

from .pie_utils import *


class PIE_Bottom_Q_alt(bpy.types.Operator):
    bl_idname = "pie.q_alt_key"
    bl_label = get_pyfilename()
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        mode = context.object.mode
        if mode == "OBJECT" or "EDIT":
            bpy.ops.view3d.localview(frame_selected=False)
        return {"FINISHED"}


classes = [
    PIE_Bottom_Q_alt,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new(PIE_Bottom_Q_alt.bl_idname, "Q", "CLICK", alt=True)
    addon_keymaps.append(km)


def unregister_keymaps():
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
