# coding=utf-8
import bpy
import math 
import bmesh
from mathutils import Vector


class NbLatticeRemoveOperator(bpy.types.Operator):
    """选择模型和晶格 移除晶格修改器"""
    bl_idname = "object.nblattice_remove_operator"
    bl_label = "NB Lattice-"

    @classmethod
    def poll(cls, context):
        a=0
        MESH_s=[]
        LATTICE_s=[]
        if context.mode == 'OBJECT':
            if len(context.selected_objects)>0:
                for i in bpy.context.selected_objects:
                    if i.type == 'MESH':
                        MESH_s.append(i)
                    if i.type == 'LATTICE':
                        LATTICE_s.append(i)  
        if len(MESH_s)>0 and len(LATTICE_s)>0:
            a=1
        return a
    
    def execute(self, context):
        
        MESH_s=[]
        LATTICE_s=[]
        if bpy.context.active_object != None:
            if bpy.context.mode == 'OBJECT':
                if len(bpy.context.selected_objects)>0:
                    for i in bpy.context.selected_objects:
                        if i.type == 'MESH':
                            MESH_s.append(i)
                        if i.type == 'LATTICE':
                            LATTICE_s.append(i)
        lattice_ob =None
       

        
        if len(LATTICE_s)>0:
            for l in LATTICE_s:
                for i in MESH_s:
                    for j in i.modifiers[:]:
                        if j.type =='LATTICE':
                            if j.object==l:
                                i.modifiers.remove(j)
       

        bpy.ops.ed.undo_push(message="NB")
        return {'FINISHED'}






classes=(
NbLatticeRemoveOperator,
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






