import bpy
from bpy.types import Menu, Operator, Panel

from ..utils import safe_register_class, safe_unregister_class
from .utils import *


class PIE_Bottom_Q_alt(Operator):
    bl_idname = "pie.q_alt_key"
    bl_label = get_pyfilename()
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.view3d.localview(frame_selected=False)
        return {"FINISHED"}


CLASSES = [
    PIE_Bottom_Q_alt,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new(PIE_Bottom_Q_alt.bl_idname, "Q", "CLICK", alt=True)
    addon_keymaps.append((km, kmi))


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
