import math
from math import pi, radians

import bmesh
import bpy
from bpy.props import FloatProperty, IntProperty
from bpy.types import Menu, Operator
from mathutils import Matrix, Quaternion, Vector

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


class VIEW3D_PIE_MT_Bottom_R(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        ob_mode = context.object.mode
        ui = context.area.ui_type
        set_pie_ridius(context, 100)
        get_orient = context.scene.transform_orientation_slots[0].type
        if ui == "VIEW_3D":
            if ob_mode == "OBJECT":
                # 4 - LEFT
                pie.operator(PIE_Transform_Rotate_Z.bl_idname, text="Z轴-90°").degree = -pi / 2
                # 6 - RIGHT
                pie.operator(PIE_Transform_Rotate_Z.bl_idname, text="Z轴+90°").degree = pi / 2
                # 2 - BOTTOM
                add_operator(pie, "pie.m4mirror", text="镜像")
                # mir.property_overridable_library_set("flick", True)
                # mir.property_overridable_library_set("remove", False)
                # mir.properties.flick = True
                # mir.properties.remove = False
                # 8 - TOP
                rotate_Y = pie.operator("transform.rotate", text="Y", icon="EVENT_Y")
                rotate_Y.orient_type = get_orient
                rotate_Y.orient_axis = "Y"
                # 7 - TOP - LEFT
                TL = pie.operator(PIE_Transform_Rotate_XY.bl_idname, text="向后转")
                TL.x = True
                TL.y = False
                TL.degree = pi / 2
                # 9 - TOP - RIGHT
                TR = pie.operator(PIE_Transform_Rotate_XY.bl_idname, text="向前转")
                TR.x = True
                TR.y = False
                TR.degree = -pi / 2
                # 1 - BOTTOM - LEFT
                TR = pie.operator(PIE_Transform_Rotate_XY.bl_idname, text="向左转")
                TR.x = False
                TR.y = True
                TR.degree = pi / 2
                # 3 - BOTTOM - RIGHT
                TR = pie.operator(PIE_Transform_Rotate_XY.bl_idname, text="向右转")
                TR.x = False
                TR.y = True
                TR.degree = -pi / 2

            elif ob_mode == "EDIT":
                # 4 - LEFT
                pie.operator(PIE_Transform_Rotate_Z.bl_idname, text="Z轴-90°").degree = -pi / 2
                # 6 - RIGHT
                pie.operator(PIE_Transform_Rotate_Z.bl_idname, text="Z轴+90°").degree = pi / 2
                # 2 - BOTTOM
                pie.operator("mesh.sort_elements", text="顶点编号排序反转").type = "REVERSE"
                # 8 - TOP
                rotate_Y = pie.operator("transform.rotate", text="Y", icon="EVENT_Y")
                rotate_Y.orient_type = get_orient
                rotate_Y.orient_axis = "Y"
                # 7 - TOP - LEFT
                TR = pie.operator(PIE_Transform_Rotate_XY.bl_idname, text="向前转")
                TR.x = True
                TR.y = False
                TR.degree = -pi / 2
                # 9 - TOP - RIGHT
                TL = pie.operator(PIE_Transform_Rotate_XY.bl_idname, text="向后转")
                TL.x = True
                TL.y = False
                TL.degree = pi / 2
                # 1 - BOTTOM - LEFT
                TR = pie.operator(PIE_Transform_Rotate_XY.bl_idname, text="向左转")
                TR.x = False
                TR.y = True
                TR.degree = pi / 2
                # 3 - BOTTOM - RIGHT
                TR = pie.operator(PIE_Transform_Rotate_XY.bl_idname, text="向右转")
                TR.x = False
                TR.y = True
                TR.degree = -pi / 2

        elif ui == "UV":
            set_pie_ridius(context, 100)
            # 4 - LEFT
            # R_Left = pie.operator("transform.rotate", text='Z轴-90°', icon='TRIA_LEFT_BAR')
            # R_Left.value = -(pi/2)
            # R_Left.orient_axis = "Z"
            # R_Left.orient_type = "VIEW"
            pie.operator(PIE_Transform_Rotate_Z.bl_idname, text="左转-90°", icon="TRIA_RIGHT_BAR").degree = -(pi / 2)

            # 6 - RIGHT
            pie.operator(PIE_Transform_Rotate_Z.bl_idname, text="右转+90°", icon="TRIA_RIGHT_BAR").degree = pi / 2
            # 2 - BOTTOM
            # 8 - TOP
            # 7 - TOP - LEFT
            # 9 - TOP - RIGHT

            # 1 - BOTTOM - LEFT
            # 3 - BOTTOM - RIGHT

        elif ui == "ShaderNodeTree":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.separator()
            # 8 - TOP
            pie.separator()
            # 7 - TOP - LEFT
            pie.separator()
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            pie.separator()
            # 3 - BOTTOM - RIGHT
            pie.separator()

        elif ui == "GeometryNodeTree":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.separator()
            # 8 - TOP
            pie.separator()
            # 7 - TOP - LEFT
            pie.separator()
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            pie.separator()
            # 3 - BOTTOM - RIGHT
            pie.separator()
        elif ui == "CompositorNodeTree":
            # 4 - LEFT
            pie.separator()
            # 6 - RIGHT
            pie.separator()
            # 2 - BOTTOM
            pie.separator()
            # 8 - TOP
            pie.separator()
            # 7 - TOP - LEFT
            pie.separator()
            # 9 - TOP - RIGHT
            pie.separator()
            # 1 - BOTTOM - LEFT
            pie.separator()
            # 3 - BOTTOM - RIGHT
            pie.separator()


class VIEW3D_PIE_MT_Ctrl_Alt_R(Menu):
    bl_label = submoduname

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius(context, 100)
        # 4 - LEFT
        pie.operator("pie.mesh_uv_rotate", text="UV左转90°").angle = 90
        # 6 - RIGHT
        pie.operator("pie.mesh_uv_rotate", text="UV右转90°").angle = -90
        # 2 - BOTTOM
        pie.separator()
        # 8 - TOP
        pie.separator()
        # 7 - TOP - LEFT
        pie.separator()
        # 9 - TOP - RIGHT
        pie.separator()
        # 1 - BOTTOM - LEFT
        pie.separator()
        # 3 - BOTTOM - RIGHT
        pie.separator()


class PIE_Transform_Rotate_Z(Operator):
    bl_idname = "pie.tramsform_rotate"
    bl_label = "Pie R 物体网格"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    degree: bpy.props.FloatProperty(name="Rotate_Dgree")  # type: ignore

    @classmethod
    def rotation_ops(self):
        bpy.ops.transform.rotate(value=self.degree, orient_axis="Z", orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)))

    def execute(self, context):
        is_pivot = context.scene.tool_settings.use_transform_pivot_point_align
        if is_pivot == True:
            is_pivot == False
            bpy.ops.transform.rotate(
                value=self.degree, orient_axis="Z", orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1))
            )
            is_pivot = True
        else:
            bpy.ops.transform.rotate(
                value=self.degree, orient_axis="Z", orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1))
            )
        return {"FINISHED"}


class PIE_Transform_Rotate_XY(Operator):
    bl_idname = "pie.uv_rotate_xy"
    bl_label = "旋转轴XY"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    x: bpy.props.BoolProperty(name="x", default=False)  # type: ignore
    y: bpy.props.BoolProperty(name="y", default=False)  # type: ignore
    degree: bpy.props.FloatProperty()  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        degree = self.degree
        use_x = self.x
        use_y = self.y
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                rotation = area.spaces.active.region_3d.view_rotation
                eul = Quaternion(rotation).to_euler()
                angle = math.degrees(eul.z)

        if -45 < angle < 45:
            if use_x:
                bpy.ops.transform.rotate(value=degree, orient_axis="X")
            elif use_y:
                bpy.ops.transform.rotate(value=degree, orient_axis="Y")
        elif 45 < angle < 135:
            if use_x:
                bpy.ops.transform.rotate(value=degree, orient_axis="Y")
            elif use_y:
                bpy.ops.transform.rotate(value=degree * -1, orient_axis="X")
        elif 135 < angle < 180 or -180 < angle < -135:
            if use_x:
                bpy.ops.transform.rotate(value=degree * -1, orient_axis="X")
            elif use_y:
                bpy.ops.transform.rotate(value=degree * -1, orient_axis="Y")
        elif -135 < angle < -45:
            if use_x:
                bpy.ops.transform.rotate(value=degree * -1, orient_axis="Y")
            elif use_y:
                bpy.ops.transform.rotate(value=degree, orient_axis="X")

        return {"FINISHED"}


class PIE_Mesh_UV_Rotate(Operator):
    """旋转UV"""

    bl_idname = "pie.mesh_uv_rotate"
    bl_label = "简单 UV 旋转"
    bl_options = {"REGISTER", "UNDO"}

    angle: bpy.props.FloatProperty(name="Angle", description="旋转角度", default=90.0, min=-360.0, max=360.0)  # type: ignore

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None and context.active_object.type == "MESH" and context.object.mode == "EDIT"
        )

    def execute(self, context):
        obj = context.active_object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        uv_layer = bm.loops.layers.uv.verify()

        # 计算选中的UV面的中心
        uv_center = Vector((0.0, 0.0))
        total_loops = 0
        for face in bm.faces:
            if face.select:
                for loop in face.loops:
                    uv_center += loop[uv_layer].uv
                    total_loops += 1
        if total_loops > 0:
            uv_center /= total_loops

        # 计算旋转矩阵
        rot_mat = Matrix.Rotation(radians(self.angle), 2)

        # 使用计算出的UV中心来旋转UV
        for face in bm.faces:
            if face.select:
                for loop in face.loops:
                    loop_uv = loop[uv_layer]
                    loop_uv.uv = rot_mat @ (loop_uv.uv - uv_center) + uv_center

        bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
        return {"FINISHED"}


class PIE_Mesh_UV_Rotate_Modal(Operator):
    """旋转UV"""

    bl_idname = "pie.mesh_uv_rotate_modal"
    bl_label = "简单 UV 旋转"
    bl_options = {"REGISTER", "UNDO"}

    initial_mouse_x: bpy.props.IntProperty()  # type: ignore
    rotation_angle: bpy.props.FloatProperty(default=0.0)  # type: ignore

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and context.active_object.mode == "EDIT"
        )

    def execute(self, context):
        self.rotate_uv(context, self.rotation_angle)
        return {"FINISHED"}

    def modal(self, context, event):
        if event.type == "MOUSEMOVE":
            delta = self.initial_mouse_x - event.mouse_x
            # 更新旋转角度，并应用-180到180度的限制
            self.rotation_angle = max(-180.0, min(180.0, self.rotation_angle - delta * 0.01))
            self.rotate_uv(context, self.rotation_angle)
            self.initial_mouse_x = event.mouse_x
        elif event.type in {"RIGHTMOUSE", "ESC", "LEFTMOUSE"}:
            return {"CANCELLED"}
        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        if context.object:
            self.initial_mouse_x = event.mouse_x
            self.rotation_angle = 0.0
            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}
        else:
            self.report({"WARNING"}, "没有激活的对象")
            return {"CANCELLED"}

    def rotate_uv(self, context, angle_degrees):
        obj = context.edit_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.verify()  # 获取或确保有 UV 层
        # 初始化变量以计算所选UV面的中心
        uv_center = [0, 0]
        total_loops = 0
        # 计算所选UV面的中心
        for face in bm.faces:
            if face.select:
                for loop in face.loops:
                    uv = loop[uv_layer].uv
                    uv_center[0] += uv.x
                    uv_center[1] += uv.y
                    total_loops += 1
        uv_center[0] /= total_loops
        uv_center[1] /= total_loops
        # 计算旋转矩阵，改为顺时针旋转
        angle_rad = -math.radians(angle_degrees)  # 注意这里的负号
        cos_angle, sin_angle = math.cos(angle_rad), math.sin(angle_rad)
        # 以所选UV面的中心为旋转中心旋转UV坐标
        for face in bm.faces:
            if face.select:
                for loop in face.loops:
                    uv = loop[uv_layer].uv
                    x, y = uv.x - uv_center[0], uv.y - uv_center[1]
                    uv.x = x * cos_angle - y * sin_angle + uv_center[0]
                    uv.y = x * sin_angle + y * cos_angle + uv_center[1]
        # 更新 bmesh
        bmesh.update_edit_mesh(me)


classes = [
    VIEW3D_PIE_MT_Bottom_R,
    PIE_Transform_Rotate_Z,
    PIE_Transform_Rotate_XY,
    PIE_Mesh_UV_Rotate,
    VIEW3D_PIE_MT_Ctrl_Alt_R,
    PIE_Mesh_UV_Rotate_Modal,
]
addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    space_name = [
        ("3D View", "VIEW_3D"),
        ("UV Editor", "EMPTY"),
        ("Node Editor", "NODE_EDITOR"),
        ("Graph Editor", "GRAPH_EDITOR"),
    ]
    for space in space_name:
        km = addon.keymaps.new(name=space[0], space_type=space[1])
        kmi = km.keymap_items.new(idname="wm.call_menu_pie", type="R", value="CLICK_DRAG")
        kmi.properties.name = "VIEW3D_PIE_MT_Bottom_R"
        addon_keymaps.append(km)

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new(idname="wm.call_menu_pie", type="R", value="CLICK_DRAG", ctrl=True, alt=True)
    kmi.properties.name = "VIEW3D_PIE_MT_Ctrl_Alt_R"

    km = addon.keymaps.new(name="Mesh")
    kmi = km.keymap_items.new(idname="pie.mesh_uv_rotate_modal", type="R", value="CLICK", ctrl=True, alt=True)


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
