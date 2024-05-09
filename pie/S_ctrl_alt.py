import math
from math import pi, radians

import bmesh
import bpy
from bpy.props import FloatProperty, IntProperty
from bpy.types import Menu, Operator
from mathutils import Matrix, Quaternion, Vector

from .utils import change_default_keymap, restored_default_keymap, set_pie_ridius

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (3, 3, 0),
    "location": "View3D",
    "category": "3D View",
}


class VIEW3D_PIE_MT_Ctrl_Alt_S(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius(context, 100)
        # 4 - LEFT
        pie.operator("pie.uv_scale_operator", text="UV缩小0.5倍").scale = 2
        # 6 - RIGHT
        pie.operator("pie.uv_scale_operator", text="UV放大2倍").scale = 0.5
        # 2 - BOTTOM
        # 8 - TOP
        V = pie.operator("pie.mesh_scale_uv", text="V向 缩放-1")
        V.scale_v = -1
        V.scale_u = 1
        # 7 - TOP - LEFT
        U = pie.operator("pie.mesh_scale_uv", text="U向 缩放-1")
        U.scale_v = 1
        U.scale_u = -1
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT


class Mesh_UVScaleModalOperator(Operator):
    """通过鼠标左右移动来调整UV缩放的大小"""

    bl_idname = "pie.uv_modal_scale_operator"
    bl_label = "调整 UV 缩放"
    bl_options = {"REGISTER", "UNDO"}

    initial_mouse_x: IntProperty()  # type: ignore
    scale_factor: FloatProperty(default=1.0, min=0.0, max=2.0)  # type: ignore

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None and context.active_object.type == "MESH" and context.object.mode == "EDIT"
        )

    def modal(self, context, event):
        if event.type == "MOUSEMOVE":
            delta = self.initial_mouse_x - event.mouse_x
            self.scale_factor = max(0.0, min(2.0, self.scale_factor - delta * 0.0002))
            self.scale_uv(context, self.scale_factor)
            self.initial_mouse_x = event.mouse_x
        elif event.type in {"RIGHTMOUSE", "ESC", "LEFTMOUSE"}:
            return {"FINISHED"}

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        if context.object:
            self.initial_mouse_x = event.mouse_x
            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}
        else:
            self.report({"WARNING"}, "没有激活的对象")
            return {"CANCELLED"}

    def scale_uv(self, context, scale_factor):
        obj = context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.verify()

        # 计算选中UV的中心点
        uv_center = [0, 0]
        selected_uv_count = 0
        for face in bm.faces:
            if face.select:  # 检查面是否被选中
                for loop in face.loops:
                    uv = loop[uv_layer].uv
                    uv_center[0] += uv[0]
                    uv_center[1] += uv[1]
                    selected_uv_count += 1

        if selected_uv_count == 0:  # 如果没有选中的UV，直接返回
            return

        uv_center[0] /= selected_uv_count
        uv_center[1] /= selected_uv_count

        # 使用计算出的UV中心进行缩放
        for face in bm.faces:
            if face.select:
                for loop in face.loops:
                    loop_uv = loop[uv_layer]
                    loop_uv.uv = (
                        (loop_uv.uv[0] - uv_center[0]) * scale_factor + uv_center[0],
                        (loop_uv.uv[1] - uv_center[1]) * scale_factor + uv_center[1],
                    )

        bmesh.update_edit_mesh(me, loop_triangles=False, destructive=False)
        return {"FINISHED"}


class Mesh_UVScaleOperator(Operator):
    bl_idname = "pie.uv_scale_operator"
    bl_label = "调整 UV 缩放"
    bl_options = {"REGISTER", "UNDO"}

    scale: FloatProperty(default=1.0, min=-100.0, max=100.0)  # type: ignore

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None and context.active_object.type == "MESH" and context.object.mode == "EDIT"
        )

    def execute(self, context):
        factor = self.scale
        obj = context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.verify()

        # 计算选中UV的中心点
        uv_center = [0, 0]
        selected_uv_count = 0
        for face in bm.faces:
            if face.select:  # 检查面是否被选中
                for loop in face.loops:
                    uv = loop[uv_layer].uv
                    uv_center[0] += uv[0]
                    uv_center[1] += uv[1]
                    selected_uv_count += 1

        if selected_uv_count == 0:  # 如果没有选中的UV，直接返回
            return

        uv_center[0] /= selected_uv_count
        uv_center[1] /= selected_uv_count

        # 使用计算出的UV中心进行缩放
        for face in bm.faces:
            if face.select:
                for loop in face.loops:
                    loop_uv = loop[uv_layer]
                    loop_uv.uv = (
                        (loop_uv.uv[0] - uv_center[0]) * factor + uv_center[0],
                        (loop_uv.uv[1] - uv_center[1]) * factor + uv_center[1],
                    )
        bmesh.update_edit_mesh(me, loop_triangles=False, destructive=False)
        return {"FINISHED"}


class PIE_ScaleUVOperator(bpy.types.Operator):
    """Scale selected faces UVs based on their center with custom scale factors"""

    bl_idname = "pie.mesh_scale_uv"
    bl_label = "Scale UV"
    bl_options = {"REGISTER", "UNDO"}

    scale_u: bpy.props.FloatProperty(name="Scale U", description="Scale U coordinates", default=1.0)  # type: ignore
    scale_v: bpy.props.FloatProperty(name="Scale V", description="Scale V coordinates", default=1.0)  # type: ignore

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None and context.active_object.type == "MESH" and context.object.mode == "EDIT"
        )

    def execute(self, context):
        obj = bpy.context.edit_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        uv_layer = bm.loops.layers.uv.verify()

        # Ensure we have UVs to scale
        if not bm.loops.layers.uv:
            self.report({"ERROR"}, "No UV Map found")
            return {"CANCELLED"}

        # Calculate the center of the selected UVs
        uv_center = Vector((0, 0))
        uv_count = 0
        for face in bm.faces:
            if face.select:
                for loop in face.loops:
                    uv = loop[uv_layer].uv
                    uv_center += uv
                    uv_count += 1
        if uv_count == 0:
            self.report({"ERROR"}, "No selected UVs to scale")
            return {"CANCELLED"}
        uv_center /= uv_count

        # Scale the UVs around the calculated center with the provided scale factors
        for face in bm.faces:
            if face.select:
                for loop in face.loops:
                    uv = loop[uv_layer].uv
                    uv.x = (uv.x - uv_center.x) * self.scale_u + uv_center.x
                    uv.y = (uv.y - uv_center.y) * self.scale_v + uv_center.y

        bmesh.update_edit_mesh(me)
        return {"FINISHED"}


def uv_menu_func(self, context):
    self.layout.operator(Mesh_UVScaleModalOperator.bl_idname)


classes = [
    Mesh_UVScaleModalOperator,
    Mesh_UVScaleOperator,
    VIEW3D_PIE_MT_Ctrl_Alt_S,
    PIE_ScaleUVOperator,
]
addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new(idname="pie.uv_modal_scale_operator", type="S", value="CLICK", ctrl=True, alt=True)

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new(idname="wm.call_menu_pie", type="S", value="CLICK_DRAG", ctrl=True, alt=True)
    kmi.properties.name = "VIEW3D_PIE_MT_Ctrl_Alt_S"


def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        # wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    bpy.types.VIEW3D_MT_uv_map.append(uv_menu_func)
    for cls in classes:
        bpy.utils.register_class(cls)
    register_keymaps()


def unregister():
    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_uv_map.remove(uv_menu_func)
