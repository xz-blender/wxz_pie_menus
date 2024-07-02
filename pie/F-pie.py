import os
import sys

import bpy
from bpy.types import Menu, Operator

from .utils import *

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


class VIEW3D_PIE_MT_Bottom_F(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        ob_type = context.object.type
        ob_mode = context.object.mode

        set_pie_ridius(context, 100)

        if ob_mode == "OBJECT":
            # 4 - LEFT
            op = pie.operator(PIE_Make_Sigle_User.bl_idname, text="单一化", icon="UNLINKED")
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.operator(Merge_Objects_WithoutActive.bl_idname, text="合并", icon="SELECT_EXTEND")
            # 8 - TOP
            add_operator(pie, "object.parent_to_empty")
            # 7 - TOP - LEFT
            if ob_type == "ARMATURE":
                pie.operator("armature.parent_clear")
            else:
                pie.operator("object.parent_clear")
            # 9 - TOP - RIGHT
            if ob_type == "ARMATURE":
                pie.operator("armature.parent_set")
            else:
                pie.operator("object.parent_set")
            # 1 - BOTTOM - LEFT
            pie.separator()
            # 3 - BOTTOM - RIGHT
            pie.operator(Clean_Custom_Normal.bl_idname, text="批量删自定法线", icon="NORMALS_VERTEX_FACE")

        if ob_mode == "EDIT":
            if ob_type == "MESH":
                # 4 - LEFT
                pie.operator("mesh.inset", text="内插面")
                # 6 - RIGHT
                add_operator(pie, "mesh.offset_edges", text="偏移边线")
                # 2 - BOTTOM
                pie.operator("mesh.subdivide", text="细分")
                # 8 - TOP
                pie.operator("mesh.separate", text="分离选中").type = "SELECTED"
                # 7 - TOP - LEFT
                pie.operator("mesh.split", text="拆分")
                # 9 - TOP - RIGHT
                add_operator(pie, "mesh.edgetools_extend", text="延伸边")
                # 1 - BOTTOM - LEFT
                pie.operator("wm.tool_set_by_id", text="切刀工具").name = "builtin.knife"
                # 3 - BOTTOM - RIGHT
                add_operator(pie, "object.mesh_edge_length_set", text="设边长")
            if ob_type == "CURVE":
                # 4 - LEFT
                pie.operator("curve.smooth", text="光滑")
                # 6 - RIGHT
                pie.operator("curvetools.add_toolpath_offset_curve", text="曲线偏移")
                # 2 - BOTTOM
                pie.operator("curve.subdivide", text="细分")
                # 8 - TOP
                pie.operator("curve.separate", text="分离")
                # 7 - TOP - LEFT
                pie.operator("curve.switch_direction", text="切换方向")
                # 9 - TOP - RIGHT

                # 1 - BOTTOM - LEFT

                # 3 - BOTTOM - RIGHT


class Clean_Custom_Normal(Operator):
    bl_idname = "pie.clear_custom_normal"
    bl_label = "Clear Custom Data"
    bl_description = "Clear Custom Data"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.object != None and context.object.type == "MESH":
            return True

    def execute(self, context):
        selection = bpy.context.selected_objects
        for o in selection:
            bpy.context.view_layer.objects.active = o
            try:
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
            except:
                None
        return {"FINISHED"}


class PIE_Make_Sigle_User(Operator):
    bl_idname = "pie.make_sigle_user"
    bl_label = "Make_Sigle_User"
    bl_description = "Make_Sigle_User Only for selected"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.object.make_single_user(object=True, obdata=True)
        return {"FINISHED"}


class Merge_Objects_WithoutActive(Operator):
    bl_idname = "pie.merge_objects_without_active"
    bl_label = "Merge Objects"
    bl_description = "Merge Objects Without Active Objects"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.object != None:
            if context.object.type in ["MESH", "CURVE", "SURFACE", "GPENCIL", "ARMATURE"]:
                return True

    def execute(self, context):
        selection_ob = context.selected_objects
        active_ob = context.active_object
        if active_ob in selection_ob:
            bpy.ops.object.join()
        else:
            context.view_layer.objects.active = selection_ob[0]
            bpy.ops.object.join()
        return {"FINISHED"}


classes = [
    VIEW3D_PIE_MT_Bottom_F,
    Clean_Custom_Normal,
    Merge_Objects_WithoutActive,
    PIE_Make_Sigle_User,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    space_name = [
        "Object Mode",
        "Mesh",
        "Curve",
    ]
    for name in space_name:
        km = addon.keymaps.new(name=name)
        kmi = km.keymap_items.new("wm.call_menu_pie", "F", "CLICK_DRAG")
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_F"
        addon_keymaps.append(km)

    km = addon.keymaps.new(name="Mesh")  # ,space_type ='VIEW_3D')
    kmi = km.keymap_items.new("mesh.vert_connect_path", "F", "CLICK", shift=True)
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


if __name__ == "__main__":
    register()
