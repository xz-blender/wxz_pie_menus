import bpy
from bpy.types import Operator

from ..utils import safe_register_class, safe_unregister_class
from .utils import *


class Mesh_Delete_By_mode(Operator):
    bl_idname = "pie.x_key"
    bl_label = get_pyfilename()
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.object.mode == "EDIT":
            return True
        else:
            return False

    def execute(self, context):
        ob_type = context.object.type
        if ob_type == "MESH":
            mode = context.tool_settings.mesh_select_mode
            # 选择模式 [点,线,面]
            if mode[0] == True:
                bpy.ops.mesh.delete(type="VERT")
            elif mode[1] == True:
                bpy.ops.mesh.delete(type="EDGE")
            elif mode[2] == True:
                bpy.ops.mesh.delete(type="FACE")
            return {"FINISHED"}

        obj = context.active_object
        if obj.type == "CURVE":

            # 获取当前编辑模式下的选中顶点
            curve_data = obj.data
            # 获取曲线对象的所有控制点
            selected_points = 0
            # 遍历曲线中的每个样条
            for spline in curve_data.splines:
                if spline.type == "BEZIER":
                    # 贝塞尔曲线的控制点
                    for point in spline.bezier_points:
                        if point.select_control_point:
                            selected_points += 1

                elif spline.type == "NURBS" or spline.type == "POLY":
                    # NURBS和多边形曲线的控制点
                    for point in spline.points:
                        if point.select:
                            selected_points += 1

            if selected_points == 1:
                bpy.ops.curve.delete(type="VERT")
            elif selected_points == 0:
                self.report({"ERROR"}, "无法删除,请选择一个顶点")
                return {"CANCELLED"}
            else:
                bpy.ops.curve.delete(type="SEGMENT")
                try:
                    bpy.ops.curvetools.operatorsplinesremovezerosegment()
                except:
                    pass
            return {"FINISHED"}


CLASSES = [
    Mesh_Delete_By_mode,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon
    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new(Mesh_Delete_By_mode.bl_idname, "X", "CLICK")
    addon_keymaps.append(km)


def unregister_keymaps():
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        for kmi in km.keymap_items:
            km.keymap_items.remove(kmi)
        # wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
