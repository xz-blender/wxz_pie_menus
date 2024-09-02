# coding=utf-8
import bpy
import math 
import bmesh
from mathutils import Vector


class NbLatticeAAOperator(bpy.types.Operator):
    """选择模型添加晶格"""
    bl_idname = "object.add_lattice_a_operator"
    bl_label = "NB Lattice"

    @classmethod
    def poll(cls, context):
        a=0
        MESH_s=[]
        ARMATURE_s=[]
        LATTICE_s=[]
        if context.mode == 'OBJECT':
            if len(context.selected_objects)>0:
                for i in bpy.context.selected_objects:
                    if i.type == 'MESH':
                        MESH_s.append(i)
                    if i.type == 'ARMATURE':
                        ARMATURE_s.append(i)
                    if i.type == 'LATTICE':
                        LATTICE_s.append(i)
        if len(MESH_s)>0 or (len(LATTICE_s)==1 and len(ARMATURE_s)==1):
            a=1    
        return a
    
    def execute(self, context):
        
        MESH_s=[]
        ARMATURE_s=[]
        LATTICE_s=[]
        if bpy.context.active_object != None:
            if bpy.context.mode == 'OBJECT':
                if len(bpy.context.selected_objects)>0:
                    for i in bpy.context.selected_objects:
                        if i.type == 'ARMATURE':
                            ARMATURE_s.append(i)
                        if i.type == 'MESH':
                            MESH_s.append(i)
                        if i.type == 'LATTICE':
                            LATTICE_s.append(i)
        lattice_ob =None
        if len(LATTICE_s)==0:
            # 计算所有选择物体的边界框
            min_corner = Vector((float('inf'), float('inf'), float('inf')))
            max_corner = Vector((-float('inf'), -float('inf'), -float('inf')))

            for obj in MESH_s:
                bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
                for corner in bbox:
                    min_corner = Vector([min(min_corner[i], corner[i]) for i in range(3)])
                    max_corner = Vector([max(max_corner[i], corner[i]) for i in range(3)])

            # 创建lattice
            lattice_name = "NBLattice"
            lattice = bpy.data.lattices.new(name=lattice_name)
            lattice_ob = bpy.data.objects.new(lattice_name, lattice)
            bpy.context.collection.objects.link(lattice_ob)

            # 设置lattice的大小
            lattice_ob.scale = (max_corner - min_corner) 

            # 将lattice移动到边界框的中心
            lattice_ob.location = (min_corner + max_corner) /2
            
            lattice_ob.select_set(True)
            
            
            for i in MESH_s:
                mod_lattice = i.modifiers.new(lattice.name, 'LATTICE')
                mod_lattice.object = lattice_ob
                i.select_set(0)

            bpy.context.view_layer.objects.active =lattice_ob
        

    
        if len(LATTICE_s)==1:
            lattice_ob=LATTICE_s[0]
            for i in MESH_s:
                haslattice=0
                for j in i.modifiers[:]:
                    if j.type =='LATTICE':
                        if j.object==lattice_ob:
                            haslattice =1
                if haslattice==0: 
                    mod_lattice = i.modifiers.new(lattice_ob.name, 'LATTICE')
                    mod_lattice.object = lattice_ob
        
        if len(ARMATURE_s)==1 and lattice_ob:
            oldactive_bone =ARMATURE_s[0].data.bones.active
            oldactive_boneName =oldactive_bone.name


            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_pattern(pattern=ARMATURE_s[0].name,extend=True)
            bpy.context.view_layer.objects.active=ARMATURE_s[0]
            bpy.ops.object.select_pattern(pattern=lattice_ob.name,extend=True)
            bpy.ops.object.parent_set(type='BONE')
            lattice_ob.users_collection[0].objects.unlink(lattice_ob)
            ARMATURE_s[0].users_collection[0].objects.link(lattice_ob)

            bpy.ops.object.mode_set(mode='POSE')
            ARMATURE_s[0].show_in_front = True


        bpy.ops.ed.undo_push(message="NB")
        return {'FINISHED'}






classes=(
NbLatticeAAOperator,
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






