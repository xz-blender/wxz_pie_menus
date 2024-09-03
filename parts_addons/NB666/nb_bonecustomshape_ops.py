from math import radians

import bmesh
import bpy
from mathutils import Matrix


class NBBoneCustomShapeOperator(bpy.types.Operator):
    """骨骼自定义形状"""

    bl_idname = "object.nb_bone_customshape_operator"
    bl_label = "NB 骨骼自定义形状"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        a = 0
        if context.active_object != None:
            if context.active_object.type == "ARMATURE":
                if context.mode == "POSE":
                    if len(context.selected_pose_bones) > 0:
                        a = 1

        return a

    def execute(self, context):

        armobj = context.active_object

        CBS_Circle = bpy.data.objects.get("NB_shape_Circle")
        if not CBS_Circle:
            mesh = bpy.data.meshes.new("CBS_Circle")
            CBS_Circle = bpy.data.objects.new("NB_shape_Circle", mesh)
            # bpy.context.collection.objects.link(basic_sphere)
            bm = bmesh.new()
            bmesh.ops.create_circle(bm, segments=32, radius=1.0)
            bm.to_mesh(mesh)
            bm.free()

        # 定义旋转矩阵（绕X轴旋转90度）
        rotation_matrix = Matrix.Rotation(radians(90), 4, "X")

        CBS_Circle_x = bpy.data.objects.get("NB_shape_Circle_x")
        if not CBS_Circle_x:
            mesh = bpy.data.meshes.new("CBS_Circle_x")
            CBS_Circle_x = bpy.data.objects.new("NB_shape_Circle_x", mesh)
            # bpy.context.collection.objects.link(basic_sphere)
            bm = bmesh.new()
            bmesh.ops.create_circle(bm, segments=32, radius=1.0, matrix=rotation_matrix)
            bm.to_mesh(mesh)
            bm.free()

        CBS_Sphere = bpy.data.objects.get("NB_shape_Sphere")
        if not CBS_Sphere:
            mesh = bpy.data.meshes.new("CBS_Sphere")
            CBS_Sphere = bpy.data.objects.new("NB_shape_Sphere", mesh)
            # bpy.context.collection.objects.link(basic_sphere)
            bm = bmesh.new()
            bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.2)
            bm.to_mesh(mesh)
            bm.free()

        CBS_Cube = bpy.data.objects.get("NB_shape_Cube")
        if not CBS_Cube:
            mesh = bpy.data.meshes.new("CBS_Cube")
            CBS_Cube = bpy.data.objects.new("NB_shape_Cube", mesh)
            # bpy.context.collection.objects.link(basic_sphere)
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=1.0)
            bm.to_mesh(mesh)
            bm.free()

        for bone in bpy.context.selected_pose_bones:
            if bone.custom_shape == None:
                bone.custom_shape = CBS_Circle
                bone.bone.show_wire = False
                if bpy.app.version[0] == 4 and bpy.app.version[1] > 1:
                    bone.custom_shape_wire_width = 1.5
            elif bone.custom_shape == CBS_Circle:
                bone.custom_shape = CBS_Circle_x
                bone.bone.show_wire = False
                if bpy.app.version[0] == 4 and bpy.app.version[1] > 1:
                    bone.custom_shape_wire_width = 1.5
            elif bone.custom_shape == CBS_Circle_x:
                bone.custom_shape = CBS_Sphere
                bone.bone.show_wire = False
            elif bone.custom_shape == CBS_Sphere:
                bone.custom_shape = CBS_Cube
                bone.bone.show_wire = True
                if bpy.app.version[0] == 4 and bpy.app.version[1] > 1:
                    bone.custom_shape_wire_width = 1.5
            else:
                bone.custom_shape = None
                bone.bone.show_wire = False
                if bpy.app.version[0] == 4 and bpy.app.version[1] > 1:
                    bone.custom_shape_wire_width = 1.0

        #        self.report({'INFO'}, "骨骼姿态")

        bpy.ops.ed.undo_push(message="NB")
        return {"FINISHED"}


addon_keymaps = []

classes = (NBBoneCustomShapeOperator,)


## 注册插件
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # 添加快捷键
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name="Window", space_type="EMPTY")
    kmi = km.keymap_items.new(
        NBBoneCustomShapeOperator.bl_idname,
        "F6",
        "PRESS",
        ctrl=False,
        shift=False,
        alt=False,
    )
    addon_keymaps.append((km, kmi))


## 注销插件
def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # 移除快捷键
    wm = bpy.context.window_manager
    # for km, kmi in addon_keymaps:
    #     km.keymap_items.remove(kmi)
    addon_keymaps.clear()


## 在启动时注册插件
if __name__ == "__main__":
    register()
