import bpy
import math 
import bmesh
import mathutils 


class NbObjectMirrorCopyOperator(bpy.types.Operator):
    """选择物体和骨架 根据物体质心添加骨骼"""
    bl_idname = "object.add_nbobjectmirrorcopyoperator"
    bl_label = "NB Object Mirror Copy"

    @classmethod
    def poll(cls, context):
        a=0
        MESH_s=[]
        ARMATURE_s=[]
       
        if context.mode == 'OBJECT':
            if len(context.selected_objects)>0:
                a=1        
                    
        return a
    
    
    def execute(self, context):
        # 获取当前选中的物体
        selected_objects = bpy.context.selected_objects
        
        
        
        def get_unique_obj_name(base_name, suffix="NB_"):
            obj_name = base_name
            count = 1
            while obj_name in selected_objects:
                obj_name = f"{suffix}{count}_{base_name}"
                count += 1
            return obj_name
        
        
        
        for obj in selected_objects:
            
            if obj.type =="MESH":
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            
            # 复制选中的物体
            R_obj = obj.copy()
            try:
                R_obj.data = obj.data.copy()
            except:
                pass
            obj.users_collection[0].objects.link(R_obj)
            
            obj_name=obj.name
            
            if obj.location.x>0:  
                obj.name =get_unique_obj_name("L_"+obj_name)
                R_obj.name =get_unique_obj_name("R_"+obj_name)
            else :
                obj.name =get_unique_obj_name("R_"+obj_name)
                R_obj.name =get_unique_obj_name("L_"+obj_name)
                
            # 进行X轴镜像变换
            scale_matrix = mathutils.Matrix.Scale(-1, 4, (1, 0, 0))
            R_obj.matrix_world = scale_matrix @ R_obj.matrix_world
            
            for ob in bpy.context.scene.objects:
                ob.select_set(False)
            bpy.context.view_layer.objects.active = R_obj
            R_obj.select_set(True)
                

            if obj.type =="MESH":
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                # 确保物体处于编辑模式
                bpy.ops.object.mode_set(mode='EDIT')            
                
                # 选择所有面
                bpy.ops.mesh.select_all(action='SELECT')

                # 修正法线
                bpy.ops.mesh.normals_make_consistent(inside=False)

                # 切换回对象模式
                bpy.ops.object.mode_set(mode='OBJECT')
           


        bpy.ops.ed.undo_push(message="NB")
        return {'FINISHED'}   
    











classes=(
NbObjectMirrorCopyOperator,
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






