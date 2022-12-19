import os
import bpy
from bpy.types import Menu, Operator
from .utils import check_rely_addon, rely_addons, set_pie_ridius
from .utils import change_default_keymap, restored_default_keymap
submoduname = __name__.split('.')[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


class PIE_MT_Bottom_A_shift(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # ob_type = context.object.type
        # ob_mode = context.object.mode

        # 4 - LEFT
        pie.operator('mesh.primitive_plane_add',
                     text='平面', icon='MESH_PLANE')
        # 6 - RIGHT
        pie.operator('mesh.primitive_cube_add', text='立方体', icon='MESH_CUBE')
        # 2 - BOTTOM
        pie.operator('curve.primitive_bezier_circle_add',
                     text='矢量圆', icon='MESH_CIRCLE')
        # 8 - TOP
        pie.operator('mesh.primitive_circle_add',
                     text='网格圆', icon='MESH_CIRCLE')
        # 7 - TOP - LEFT
        pie.operator('mesh.primitive_vert_add', text='网格点', icon='DOT')
        # 9 - TOP - RIGHT
        pie.operator('curve.simple', text='矢量点',
                     icon='DOT')
        # 1 - BOTTOM - LEFT
        pie.operator('mesh.primitive_cylinder_add',
                     text='柱', icon='MESH_CYLINDER')
        # 3 - BOTTOM - RIGHT
        pie.operator('mesh.primitive_uv_sphere_add',
                     text='球', icon='MESH_UVSPHERE')


classes = [
    PIE_MT_Bottom_A_shift,

]


addon_keymaps = []

def toggle_keymap(value):
    keys = bpy.context.window_manager.keyconfigs.default.keymaps['Object Mode'].keymap_items.items()
    a_list = []
    for name,data in keys:
        if name == 'wm.call_menu':
            a_list.append(data)
    for key in a_list:
        if key.name == 'Add':
            key.value = value
    a_list.clear()

def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", "A",
                              "CLICK_DRAG", shift=True)
    kmi.properties.name = "PIE_MT_Bottom_A_shift"
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
            print(__name__,'->',cls,' error')
    register_keymaps()

    toggle_keymap('CLICK')


def unregister():
    toggle_keymap('PRESS')

    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()
#     bpy.ops.wm.call_menu_pie(name="PIE_MT_Bottom_A")
