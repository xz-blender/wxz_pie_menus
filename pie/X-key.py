import bpy
from bpy.types import Operator
from .utils import change_default_keymap, restored_default_keymap

submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "KEY"}


class Mesh_Delete_By_mode(Operator):
    bl_idname = "pie.x_key"
    bl_label = "删除点线面"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        ob_type = context.object.type
        ob_mode = context.object.mode
        if ob_type == "MESH" and ob_mode == "EDIT":
            return True
        else:
            return False

    def execute(self, context):
        mode = context.tool_settings.mesh_select_mode
        #选择模式 [点,线,面]
        if mode[0] == True:
            bpy.ops.mesh.delete(type='VERT')
        elif mode[1] == True:
            bpy.ops.mesh.delete(type='EDGE')
        elif mode[2] == True:
            bpy.ops.mesh.delete(type='FACE')

        return {"FINISHED"}


classes = [
    Mesh_Delete_By_mode,
]

addon_keymaps = []

def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new(Mesh_Delete_By_mode.bl_idname, 'X', 'CLICK')
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

    global key1
    key1 = change_default_keymap(
        'Object Mode','object.delete',
        [('value','CLICK')],
        [('use_global',False),('confirm',False)]
        )

    global key2
    key2 = change_default_keymap(
        'Mesh','wm.call_menu',
        [('value','CLICK'),('active',False)]
        )


def unregister():
    unregister_keymaps()

    restored_default_keymap(key1)
    restored_default_keymap(key2)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()
