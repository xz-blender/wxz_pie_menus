import bpy
import math 
import bmesh
import mathutils 
from mathutils import Matrix
from math import radians

class NB_simpleparent_Operator(bpy.types.Operator):
    """选择物体 快速添加多级别父级骨骼绑定"""
    bl_idname = "object.nbsimpleparentoperator"
    bl_label = "nb simple parent"
    
    hierarchy: bpy.props.IntProperty(
        name="hierarchy",
        description="hierarchy",
        default=3,
        min=1,
        max=6
    )
    
    
    def invoke(self, context,event):
        wm =context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        row = column.row(align=True)
        row.prop(self, "hierarchy")

        
    @classmethod
    def poll(cls, context):
        a=0

        if context.active_object != None:
            if len(bpy.context.selected_objects[:])==1:
                if bpy.context.mode =='OBJECT':
                    a=1
                    
            if context.active_object.type == 'ARMATURE':
                if context.mode == 'EDIT_ARMATURE':
                    if len(context.selected_bones)>0:
                        a=1
                    
        return a

    def execute(self, context):

        if bpy.context.mode =='OBJECT':

            # 获取激活的对象（假设你只激活了一个对象）
            active_object = bpy.context.active_object
            active_object.animation_data_clear()
            bpy.ops.object.select_all(action='DESELECT')

            armName =active_object.name+"_Arm"
            arm = bpy.data.armatures.new(armName)
            o=bpy.data.objects.new(armName,arm)
            bpy.context.scene.collection.objects.link(o)
            
            o.show_in_front = True
            bpy.context.view_layer.objects.active=o
            o.matrix_world=active_object.matrix_world
            
            bpy.ops.object.mode_set(mode='EDIT')
            
            Allbones=[]
            max_dimension=max(active_object.dimensions)
            if max_dimension==0:
                max_dimension=1
            
            for i in range(self.hierarchy):
                bone1Name =active_object.name+"_"+str(i)
                bone1 =arm.edit_bones.new(bone1Name)
                bone1.head =(0.0, 0.0, 0.0)
                
                y=max_dimension/max(active_object.scale)/2
                y+=i*0.33
                bone1.tail =(0.0, y, 0.0)
                Allbones.append(bone1)
                
            for i,bone in enumerate(Allbones):
                if i<len(Allbones)-1:
                    bone.parent =Allbones[i+1]
                
            
            bpy.ops.object.mode_set(mode='POSE')
                    
             # 定义旋转矩阵（绕X轴旋转90度）
            rotation_matrix = Matrix.Rotation(radians(90), 4, 'X')

            CBS_Circle_x=bpy.data.objects.get("NB_shape_Circle_x")
            if not CBS_Circle_x :         
                mesh = bpy.data.meshes.new('CBS_Circle_x')
                CBS_Circle_x = bpy.data.objects.new("NB_shape_Circle_x", mesh)
                #bpy.context.collection.objects.link(basic_sphere)
                bm = bmesh.new()
                bmesh.ops.create_circle(bm,segments=32, radius=1.0,matrix=rotation_matrix)
                bm.to_mesh(mesh)
                bm.free()         
            
            for i in range(self.hierarchy):
                o.pose.bones[active_object.name+"_"+str(i)].custom_shape = CBS_Circle_x
                o.pose.bones[active_object.name+"_"+str(i)].rotation_mode = 'XYZ'
                if bpy.app.version[0]==4 and bpy.app.version[1]>1:
                    o.pose.bones[active_object.name+"_"+str(i)].custom_shape_wire_width = 1.5

            o.data.bones[active_object.name+"_"+str(self.hierarchy-1)].select =True
            
            active_object.parent = o
            active_object.parent_type = 'BONE'
            active_object.parent_bone = active_object.name+"_0"
            
            active_object.location[0] = 0
            active_object.location[1] = -max_dimension/max(active_object.scale)/2
            active_object.location[2] = 0
            
            active_object.rotation_mode = 'XYZ'
            active_object.rotation_euler[0] = 0
            active_object.rotation_euler[1] = 0
            active_object.rotation_euler[2] = 0
            active_object.scale[0] = 1
            active_object.scale[1] = 1
            active_object.scale[2] = 1

            active_object.lock_location[0] = True
            active_object.lock_location[1] = True
            active_object.lock_location[2] = True
            
            active_object.lock_rotation[0] = True
            active_object.lock_rotation[1] = True
            active_object.lock_rotation[2] = True
            
            active_object.lock_scale[0] = True
            active_object.lock_scale[1] = True
            active_object.lock_scale[2] = True

        if context.mode == 'EDIT_ARMATURE':
            selBoneName_s =[]
            for i in bpy.context.selected_bones:
                selBoneName_s.append(i.name)
                
            arm =bpy.context.object.data
            
            def adv_rename(string,insertname):
    #            prefixes = ["left", "right", "l_", "r_", "l.", "r.", "l-", "r-", "l ", "r "]
                suffixes = ["left", "right", "_l", "_r", ".l", ".r", "-l", "-r", " l", " r"]
                # 检查字符串是否以指定的后缀结尾
                if any(string.lower().endswith(suffix) for suffix in suffixes):
                    # 找到后缀的位置
                    suffix_index = len(string)
                    for suffix in suffixes:
                        if string.lower().endswith(suffix):
                            suffix_index -= len(suffix)
                            break
                    # 在后缀前插入"_mingcheng"
                    newName = string[:suffix_index] + insertname + string[suffix_index:]

                else:
                    newName=string+ insertname 
                return newName
            
            # 获取骨骼的方向向量的函数
            def get_bone_direction(bone):
                # 骨骼方向通过头部到尾部的向量计算
                direction = bone.tail - bone.head
                return direction.normalized()
            
            
            def create_offset_bone(bone1,t=1):
                for i in range(t):
                    bone_p_name =adv_rename(bone1.name,"_off")
                    bone_p =arm.edit_bones.new(bone_p_name)
                    bone_p.head =bone1.head
                    bone_p.tail =bone1.head+get_bone_direction(bone1)*bone1.length*1.2
                    bone_p.use_deform = False
                    bone_p.roll=bone1.roll
                    bone_p.parent =bone1.parent
                    bone_p.bbone_x = bone1.bbone_x*0.8
                    bone_p.bbone_z = bone1.bbone_z*0.8
                    bone1.parent =bone_p
                    bone1=bone_p
                  
                    
            for i in selBoneName_s:  
                bone1=arm.edit_bones.get(i) 
                create_offset_bone(bone1,self.hierarchy)
                
                
            bpy.ops.object.mode_set(mode='POSE')    
                
        bpy.ops.ed.undo_push(message="NB")       
        return {'FINISHED'}




classes=(
NB_simpleparent_Operator,
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






