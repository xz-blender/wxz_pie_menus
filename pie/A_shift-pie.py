import bpy
from bpy.types import Menu, Operator

from .pie_utils import *


class PIE_MT_Bottom_A_shift(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius()

        # 4 - LEFT
        pie.operator("mesh.primitive_plane_add", text="平面", icon="MESH_PLANE")
        # 6 - RIGHT
        pie.operator("mesh.primitive_cube_add", text="立方体", icon="MESH_CUBE")
        # 2 - BOTTOM
        add_operator(pie, "curve.primitive_bezier_circle_add", text="矢量圆", icon="MESH_CIRCLE")
        # 8 - TOP
        pie.operator("mesh.primitive_circle_add", text="网格圆", icon="MESH_CIRCLE")
        # 7 - TOP - LEFT
        add_operator(pie, "mesh.primitive_vert_add", text="网格点", icon="DOT")
        # 9 - TOP - RIGHT
        add_operator(pie, "curve.simple", text="矢量点", icon="DOT")
        # 1 - BOTTOM - LEFT
        pie.operator("mesh.primitive_cylinder_add", text="柱", icon="MESH_CYLINDER")
        # 3 - BOTTOM - RIGHT
        pie.operator("mesh.primitive_uv_sphere_add", text="球", icon="MESH_UVSPHERE")


classes = [
    PIE_MT_Bottom_A_shift,
]
class_register, class_unregister = bpy.utils.register_classes_factory(classes)
addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", "A", "CLICK_DRAG", shift=True)
    kmi.properties.name = "PIE_MT_Bottom_A_shift"
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
