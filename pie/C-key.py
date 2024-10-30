import bpy
from bpy.types import Menu, Operator

from .pie_utils import *

# class PIE_C_KEY(Operator):
#     bl_idname = get_pyfilename()
#     bl_label = "C-key"
#     bl_options = {"REGISTER"}

#     @classmethod
#     def poll(cls, context):
#         return True

#     def execute(self, context):

#         return {"FINISHED"}


classes = [
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
        addon_keymaps.append(km)


def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        # wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    register_keymaps()


def unregister():
    unregister_keymaps()
