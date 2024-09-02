import bpy
import math 
import bmesh
import mathutils 

class NB_selall_update_driver_Operator(bpy.types.Operator):
    """所选物体驱动器更新依赖"""
    bl_idname = "object.selallupdatedriveroperator"
    bl_label = "select update driver "
    
    
    @classmethod
    def poll(cls, context):
        a=0
        
        obj = bpy.context.selected_objects
        if  obj != None:
            a=1
        return a

    def execute(self, context):
        objects = bpy.context.selected_objects
        # 遍历所有对象
        for obj in objects:
            animadata=obj.animation_data
            if animadata:
                for v in obj.animation_data.drivers.values():
                    fc =v
                    fc.driver.expression+=" "
                    fc.driver.expression = fc.driver.expression[:-1]
                
        bpy.ops.ed.undo_push(message="NB")
        return {'FINISHED'}




classes=(
NB_selall_update_driver_Operator,
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






