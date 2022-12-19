import bpy
import os
from bpy.types import Menu, Operator
from .utils import set_pie_ridius, change_default_keymap, restored_default_keymap

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


# class PIE_C_KEY(Operator):
#     bl_idname = "pie.c_key"
#     bl_label = "C-key"
#     bl_options = {"REGISTER"}

#     @classmethod
#     def poll(cls, context):
#         return True

#     def execute(self, context):
#         ui = context.area.ui_type
#         if ui == 'VIEW_3D':
#             mode = context.object.mode
#             if mode in ['OBJECT', 'EDIT']:
#                 bpy.ops.wm.tool_set_by_id(name='builtin.select_circle')
#         elif ui == 'UV':
#             bpy.ops.wm.tool_set_by_id(name='builtin.select_circle')
#         return {"FINISHED"}


classes = [
    # PIE_C_KEY,
]

addon_keymaps = []

def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    space_name = {
        '3D View':'VIEW_3D',
        'UV Editor':'IMAGE_EDITOR',
        'Node Editor':'NODE_EDITOR',
        'Graph Editor':'GRAPH_EDITOR'
    }
    for name,space in space_name.items():
        km = addon.keymaps.new(name=name,space_type=space)
        kmi = km.keymap_items.new('wm.tool_set_by_id', 'C', 'CLICK')
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
    # for cls in classes:
    #     bpy.utils.register_class(cls)
    register_keymaps()

    global key1
    key1 = change_default_keymap(
        '3D View','view3d.select_circle',
        [('active',False)],
        )
    global key2
    key2 = change_default_keymap(
        'UV Editor','uv.select_circle',
        [('active',False)],
        )
    global key3
    key3 = change_default_keymap(
        'Node Editor','node.select_circle',
        [('active',False)],
        )
    global key4
    key4 = change_default_keymap(
        'Graph Editor','graph.select_circle',
        [('active',False)],
        )


def unregister():
    restored_default_keymap(key1)
    restored_default_keymap(key2)
    restored_default_keymap(key3)
    restored_default_keymap(key4)

    unregister_keymaps()
    # for cls in reversed(classes):
    #     bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()