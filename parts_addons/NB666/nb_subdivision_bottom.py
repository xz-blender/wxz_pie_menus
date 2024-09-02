import bpy
import math 
import bmesh
import mathutils 


class NbSubdivisionBottomOperator(bpy.types.Operator):
    """细分修改器移至底部"""
    bl_idname = "object.nbsubdivisionbottomoperator"
    bl_label = "Subdivision Bottom"


    @classmethod
    def poll(cls, context):
        a=0
        MESH_s=[] 
        if context.mode == 'OBJECT':
            if len(context.selected_objects)>0:
                for i in bpy.context.selected_objects:
                    if i.type == 'MESH':
                        MESH_s.append(i)
        if len(MESH_s)>0:
            a=1
                
                    
        return a
    
    
    def execute(self, context):
        MESH_s=[]       
        for i in bpy.context.selected_objects:
            if i.type == 'MESH':
                MESH_s.append(i)

        for obj in MESH_s:
            if len(obj.modifiers)>0:
                subM=[]
                subM_id=[]
                for i,m in enumerate(obj.modifiers):
                    if m.type =='SUBSURF':
                        subM.append(m)
                        subM_id.append(i)
                if len(subM)>0:
                    obj.modifiers.move(subM_id[-1],len(obj.modifiers[:])-1)
    
    
    
        bpy.ops.ed.undo_push(message="NB")
        return {'FINISHED'}   
    





classes=(
NbSubdivisionBottomOperator,
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






