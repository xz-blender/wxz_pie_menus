import bpy
from bpy.types import Menu, Operator

from ..utils import safe_register_class, safe_unregister_class
from .utils import *

# class PIE_C_KEY(Operator):
#     bl_idname = get_pyfilename()
#     bl_label = "C-key"
#     bl_options = {"REGISTER"}

#     @classmethod
#     def poll(cls, context):
#         return True

#     def execute(self, context):

#         return {"FINISHED"}


CLASSES = [
    # PIE_C_KEY,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    space_name = {
        "3D View": "VIEW_3D",
        "UV Editor": "IMAGE_EDITOR",
        "Node Editor": "NODE_EDITOR",
        "Graph Editor": "GRAPH_EDITOR",
    }
    for name, space in space_name.items():
        km = addon.keymaps.new(name=name, space_type=space)
        kmi = km.keymap_items.new("wm.tool_set_by_id", "C", "CLICK")
        kmi.properties.name = "builtin.select_circle"
        addon_keymaps.append((km, kmi))


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
