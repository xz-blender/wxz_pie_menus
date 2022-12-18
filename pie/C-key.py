import bpy
import os
from bpy.types import Menu, Operator
from .utils import set_pie_ridius

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


class PIE_C_KEY(Operator):
    bl_idname = "pie.c_key"
    bl_label = "C-key"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        ui = context.area.ui_type
        if ui == 'VIEW_3D':
            mode = context.object.mode
            if mode in ['OBJECT', 'EDIT']:
                bpy.ops.wm.tool_set_by_id(name='builtin.select_circle')
        elif ui == 'UV':
            bpy.ops.wm.tool_set_by_id(name='builtin.select_circle')
        return {"FINISHED"}


classes = [
    PIE_C_KEY,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    space_name = [
        '3D View',
        'UV Editor',
    ]
    for name in space_name:
        km = addon.keymaps.new(name=name)
        kmi = km.keymap_items.new(PIE_C_KEY.bl_idname, 'C', 'CLICK')
        addon_keymaps.append(km)

    # km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    # kmi = km.keymap_items.new(PIE_C_KEY.bl_idname, 'C', 'CLICK')
    # addon_keymaps.append(km)


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
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_C")
