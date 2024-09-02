import bpy
import math 
import bmesh
import mathutils 


class NbObjectBoneOperator(bpy.types.Operator):
    """选择物体和骨架 根据物体质心添加骨骼"""
    bl_idname = "object.add_nbobjectboneoperator"
    bl_label = "NB Object Bone Ctrl"

    @classmethod
    def poll(cls, context):
        a=0
        MESH_s=[]
        ARMATURE_s=[]
       
        if context.mode == 'OBJECT':
            if len(context.selected_objects)>0:
                for i in bpy.context.selected_objects:
                    if i.type == 'ARMATURE':
                        ARMATURE_s.append(i)    
        if len(ARMATURE_s)==1:
            a=1        
                    
        return a
    
    
    def execute(self, context):
        MESH_s=[]
        for i in bpy.context.selected_objects:
                    if i.type == 'MESH':
                        MESH_s.append(i)    
        
        # 获取当前选中的物体
        selected_objects = bpy.context.selected_objects
        

        # 在选中的物体中找到一个骨架物体
        armature = None
        for obj in selected_objects:
            if obj.type == 'ARMATURE':
                armature = obj
                break

        # 如果没有找到骨架物体，抛出错误
        if armature is None:
            raise TypeError("选中的物体中必须包含一个骨架 (Armature)")


        armature.show_in_front = True

        # 移除骨架物体以外的选中的物体
        selected_objects.remove(armature)

        # 设置骨架的位置在世界坐标原点
        armature.location = (0, 0, 0)

        selected_objects = MESH_s
        has_arm_objs=[]
        for obj in selected_objects:
            # 检查是否已有骨架修改器
            has_armature_modifier = False
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE' and modifier.object == armature:
                    has_armature_modifier = True
                    break
            # 如果有骨架修改器
            if has_armature_modifier:
                has_arm_objs.append(obj)
                
        for obj in has_arm_objs:        
            selected_objects.remove(obj)


        # 进入编辑模式
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')
        armature_data = armature.data

        def get_unique_bone_name(base_name, suffix="NB_"):
            bone_name = base_name
            count = 1
            while bone_name in armature_data.edit_bones:
                bone_name = f"{suffix}{count}_{base_name}"
                count += 1
            return bone_name

        # 创建骨骼并对齐到每个选中的物体
        for obj in selected_objects:
            # 获取物体的位置和矩阵
            obj_location = obj.location
            obj_matrix = obj.matrix_world
            
            # 检测物体上是否有镜像修改器
            has_mirror_modifier = False
            mirror_axis_x = False
            for modifier in obj.modifiers:
                if modifier.type == 'MIRROR':
                    has_mirror_modifier = True
                    mirror_axis_x = modifier.use_axis[0]  # 检查X轴镜像
            
            # 确定骨骼的初始名称
            base_bone_name = obj.name
            
            # 检查重名并添加后缀
            bone_name = get_unique_bone_name(base_bone_name)
            
            # 如果有镜像并且名字中没有_L或_R，则添加_L后缀
            if has_mirror_modifier and mirror_axis_x:
                if "_L" not in bone_name and "_R" not in bone_name:
                    bone_name += "_L"
                elif "_R" in bone_name:
                    bone_name = bone_name.replace("_R", "_L")
            
            # 获取唯一的骨骼名称
            bone_name = get_unique_bone_name(bone_name)
            
            bone = armature_data.edit_bones.new(bone_name)
            bone.parent =armature_data.edit_bones.active
            
            # 设置骨骼的头和尾的位置
            bone.head = obj_location
            bone.tail = obj_location + mathutils.Vector((0, 0, 1))*obj.dimensions[1]*0.55  # 初始尾部位置
            
            # 对齐骨骼到物体的局部坐标
            bone_matrix = obj_matrix.to_3x3().to_4x4()
            bone_matrix.translation = obj_location
            bone.matrix = bone_matrix
            
            # 如果有镜像修改器并且是X轴镜像，则创建对称的骨骼
            if has_mirror_modifier and mirror_axis_x:
                sym_base_bone_name = bone_name.replace("_L", "_R")
                
                # 获取唯一的对称骨骼名称
                sym_bone_name = get_unique_bone_name(sym_base_bone_name)
                
                sym_bone = armature_data.edit_bones.new(sym_bone_name)
                sym_bone.parent =armature_data.edit_bones.active

                sym_bone.head = (-obj_location.x, obj_location.y, obj_location.z)
                sym_bone.tail = (-bone.tail.x,bone.tail.y,bone.tail.z)
                sym_bone.roll = -bone.roll
            
            # 返回对象模式
            bpy.ops.object.mode_set(mode='OBJECT')
            
            
            armature_modifier = obj.modifiers.new(name='Armature', type='ARMATURE')
            armature_modifier.object = armature
            
            # 创建顶点组并将所有顶点分配给这个组
            if obj.type == 'MESH':
                vertex_group = obj.vertex_groups.new(name=bone_name)
                mesh = obj.data
                
                # 分配所有顶点给顶点组
                vertex_indices = [v.index for v in mesh.vertices]
                vertex_group.add(vertex_indices, 1.0, 'ADD')
                
                # 为对称骨骼创建顶点组
                if has_mirror_modifier and mirror_axis_x:
                    sym_vertex_group = obj.vertex_groups.new(name=sym_bone_name)
                    sym_vertex_group.add(vertex_indices, 0.0, 'ADD')
            
            # 再次进入编辑模式以继续创建新的骨骼
            bpy.ops.object.mode_set(mode='EDIT')
            
            obj.select_set(0)

        # 返回对象模式
        bpy.ops.object.mode_set(mode='POSE')
       
       
        bpy.ops.ed.undo_push(message="NB")
        return {'FINISHED'}   
    











classes=(
NbObjectBoneOperator,
)

## 注册插件
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

## 注销插件
def unregister():

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

## 在启动时注册插件
if __name__ == "__main__":
    register()






