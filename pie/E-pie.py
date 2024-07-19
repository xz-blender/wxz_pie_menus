import os

import bmesh
import bpy
from bpy.types import Menu, Operator, Panel, PropertyGroup

from .utils import *

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "PIE",
}


class VIEW3D_PIE_MT_Bottom_E(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        layout.alignment = "CENTER"
        pie = layout.menu_pie()

        ob_type = context.object.type
        ob_mode = context.object.mode

        set_pie_ridius(context, 100)

        if ob_mode == "EDIT" and ob_type == "MESH":
            # 4 - LEFT
            pie.operator("mesh.flip_normals")
            # 6 - RIGHT
            col = pie.split().box().column(align=True)
            col.scale_y = 1.1
            col.operator("pie.mm_fuse")
            col.operator("pie.mm_change_width")
            col.operator("pie.mm_unchamfer")
            col.operator("pie.mm_turn_corner")
            col.operator("pie.mm_quad_corner")
            col.separator(factor=0.1)
            col.operator("pie.mm_unfuse")
            col.operator("pie.mm_refuse")
            col.operator("pie.mm_unbevel")
            col.separator(factor=0.1)
            col.operator("pie.mm_offset_cut")
            col.operator("pie.mm_unfuck")
            col.operator("pie.mm_boolean_cleanup")
            col.separator(factor=0.1)
            col.operator("pie.mm_symmetrize")
            # 2 - BOTTOM
            pie.operator("mesh.normals_make_consistent")
            # 8 - TOP
            pie.operator("mesh.extrude_manifold", text="挤出流形")
            # 7 - TOP - LEFT
            pie.operator("mesh.bridge_edge_loops", text="桥接循环边")
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            col = pie.split().box().column()
            add_operator(col, "mesh.set_edge_flow")
            add_operator(col, "mesh.set_edge_linear")
            # 3 - BOTTOM - RIGHT
            pie.separator()

        if ob_mode == "OBJECT" and ob_type == "MESH":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.operator("pie.ke_lineararray")
            # 2 - BOTTOM
            pie.separator()
            # 8 - TOP
            pie.operator("pie.ke_radial_instances")
            # 7 - TOP - LEFT
            # 9 - TOP - RIGHT
            # 1 - BOTTOM - LEFT
            # 3 - BOTTOM - RIGHT


class PIE_Shift_E_KEY(Operator):
    bl_idname = "pie.shift_e"
    bl_label = "设置折痕"
    bl_description = "在不同网格选择模式下设置不同的折痕"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.mode == "EDIT_MESH"

    def execute(self, context):
        active_ob_data = context.active_object.data
        for edge in active_ob_data.edges:
            if edge.select == True:
                edge.crease = 1

        return {"FINISHED"}


class PIE_Ctrl_Shift_E_KEY(Operator):
    bl_idname = "pie.ctrl_shift_e"
    bl_label = "设置权重"
    bl_description = "在不同网格选择模式下设置不同的权重"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.mode == "EDIT_MESH"

    def execute(self, context):

        return {"FINISHED"}


classes = [
    VIEW3D_PIE_MT_Bottom_E,
    PIE_Shift_E_KEY,
    PIE_Ctrl_Shift_E_KEY,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", "E", "CLICK_DRAG")
    kmi.properties.name = "VIEW3D_PIE_MT_Bottom_E"
    addon_keymaps.append(km)

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new("pie.shift_e", "E", "PRESS", shift=True)
    addon_keymaps.append(km)

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new("pie.ctrl_shift_e", "E", "PRESS", ctrl=True, shift=True)
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


def unregister():

    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
#     register()
#     bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_MT_Bottom_E")
