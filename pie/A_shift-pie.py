import bmesh
import bpy
import mathutils
from bpy.props import BoolProperty, FloatProperty, StringProperty
from bpy.types import Menu, Operator

from ..utils import safe_register_class, safe_unregister_class
from .utils import *


class PIE_MT_Bottom_A_shift(Menu):
    bl_label = get_pyfilename()

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        set_pie_ridius()
        ob_mode = get_ob_mode(context)
        ob_type = get_ob_type(context)

        # 4 - LEFT
        pie.operator("mesh.primitive_plane_add", text="平面", icon="MESH_PLANE")
        # 6 - RIGHT
        pie.operator("mesh.primitive_cube_add", text="立方体", icon="MESH_CUBE")
        # 2 - BOTTOM
        if ob_mode == "EDIT" and ob_type == "MESH":
            pie.operator("pie.add_area_light_from_rectancle_face", text="添加同面光", icon="LIGHTPROBE_PLANE")
        else:
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


class PIE_Add_Area_Light_From_Rectancle_Face(Operator):
    bl_idname = "pie.add_area_light_from_rectancle_face"
    bl_label = "添加激活面同大小的区域光"
    bl_description = "添加激活面同大小的区域光"
    bl_options = {"REGISTER", "UNDO"}

    normal_move_offset: FloatProperty(name="位置偏移", default=0.01)  # type: ignore
    invert_normal: BoolProperty(name="翻转灯光法向", default=False)  # type: ignore
    new_data: BoolProperty(name="新灯光", default=False)  # type: ignore

    instant_mesh: StringProperty(name="灯光数据名称", default="Area_Light")  # type: ignore

    @classmethod
    def poll(cls, context):
        return context.object.mode == "EDIT"

    def draw(self, context):

        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"
        col = layout.box().column()
        col.alignment = "RIGHT"
        col.prop(self, "normal_move_offset")
        col.prop(self, "invert_normal")

        box = layout.box()
        row = box.row()
        row.prop(self, "new_data")
        row = box.row()
        if self.new_data:
            row.prop(self, "instant_mesh", icon="LIGHT", text="新建数据名")
        else:
            row.prop_search(self, "instant_mesh", bpy.data, "lights", text="选择数据")

    def execute(self, context):
        ob_mode = get_ob_mode(context)
        ob_type = get_ob_type(context)
        obj = bpy.context.active_object
        # 检查激活对象是否为网格
        if obj is None or ob_type != "MESH":
            self.report({"ERROR"}, "请在网格对象的编辑模式下运行此脚本")
            return {"CANCELLED"}
        else:
            # 确保处于编辑模式
            if ob_mode != "EDIT":
                self.report({"ERROR"}, "请在编辑模式下运行此脚本")
                return {"CANCELLED"}
            else:
                bm = bmesh.from_edit_mesh(obj.data)
                # 获取选中的面
                selected_faces = [f for f in bm.faces if f.select]
                if len(selected_faces) != 1:
                    self.report({"ERROR"}, "请选择一个四边面（且只选一个）")
                    return {"CANCELLED"}
                else:
                    face = selected_faces[0]
                    if len(face.verts) != 4:
                        self.report({"ERROR"}, "请选择一个四边面（非三角面）")
                        return {"CANCELLED"}
                    else:
                        # 获取面的顶点坐标（在世界坐标系中）
                        verts_world = [obj.matrix_world @ v.co for v in face.verts]
                        # 计算面的中心位置
                        face_center = sum(verts_world, mathutils.Vector()) / 4.0
                        # 计算面的法线（在世界坐标系中）
                        if self.invert_normal:
                            normal_world = obj.matrix_world.to_quaternion() @ face.normal
                        else:
                            normal_world = obj.matrix_world.to_quaternion() @ -face.normal
                        # 计算面的U和V方向，用于确定灯光的旋转
                        edge1 = verts_world[1] - verts_world[0]
                        edge2 = verts_world[2] - verts_world[1]
                        u_dir = edge1.normalized()
                        v_dir = edge2.normalized()
                        # 计算与 normal_world 和 u_dir 正交的 y_axis
                        y_axis = normal_world.cross(u_dir).normalized()
                        # 设置灯光的位置
                        location = face_center + normal_world * (
                            self.normal_move_offset if self.invert_normal else -self.normal_move_offset
                        )
                        # 切换到对象模式（仅在必要时）
                        if bpy.context.mode != "OBJECT":
                            bpy.ops.object.mode_set(mode="OBJECT")
                        # 为灯光对象创建唯一名称，基于对象名称
                        light_object_name = f"{obj.name}_{self.instant_mesh}"

                        # 创建灯光数据
                        def create_light_data():
                            name = self.instant_mesh
                            if bpy.data.lights.get(name):
                                light_data = bpy.data.lights[name]
                            else:
                                light_data = bpy.data.lights.new(name=name, type="AREA")
                                light_data.shape = "RECTANGLE"
                            return light_data

                        light_data = create_light_data()
                        light_data.size = 1
                        light_data.size_y = 1
                        # 创建灯光对象
                        light_object = bpy.data.objects.new(light_object_name, light_data)
                        bpy.context.collection.objects.link(light_object)

                        if self.instant_mesh:
                            light_data.name = self.instant_mesh
                        # 计算灯光的旋转，使其与面对齐
                        # 构建旋转矩阵
                        matrix = mathutils.Matrix(
                            (
                                u_dir.to_4d(),
                                y_axis.to_4d(),
                                normal_world.normalized().to_4d(),
                                mathutils.Vector((0.0, 0.0, 0.0, 1.0)),
                            )
                        ).transposed()
                        light_object.matrix_world = mathutils.Matrix.Translation(location) @ matrix.to_3x3().to_4x4()
                        # 计算灯光尺寸，考虑缩放
                        width = (verts_world[1] - verts_world[0]).length
                        height = (verts_world[2] - verts_world[1]).length
                        light_object.scale = (width, height, 1)
                        # 将原对象设置为激活对象
                        bpy.context.view_layer.objects.active = obj
                        if bpy.context.mode != "EDIT_MESH":
                            bpy.ops.object.mode_set(mode="EDIT")

                        return {"FINISHED"}


CLASSES = [
    PIE_MT_Bottom_A_shift,
    PIE_Add_Area_Light_From_Rectancle_Face,
]

addon_keymaps = []


def register_keymaps():
    addon = bpy.context.window_manager.keyconfigs.addon

    km = addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new("wm.call_menu_pie", "A", "CLICK_DRAG", shift=True)
    kmi.properties.name = "PIE_MT_Bottom_A_shift"
    addon_keymaps.append((km, kmi))


def register():
    safe_register_class(CLASSES)
    register_keymaps()


def unregister():
    keymap_safe_unregister(addon_keymaps)
    safe_unregister_class(CLASSES)
