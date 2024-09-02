import bpy
import math 
import bmesh
import mathutils 


class fibonacciBoneOperator(bpy.types.Operator):
    """斐波那契 骨骼编辑模式 选择骨骼 给骨骼创建有序分段"""
    bl_idname = "object.fibonacciboneoperator"
    bl_label = "fibonacci Bone"
#    bl_description = "斐波那契aaa"
#    bl_options = {"REGISTER", "UNDO"}

    number: bpy.props.IntProperty(name='Number', default=10, min=2, max=20)
    power: bpy.props.FloatProperty(name='Power', default=0.25, min=0, max=1)

    def invoke(self, context,event):
        wm =context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="分段")
        column = layout.column()

        row = column.row(align=True)
        row.prop(self, "number")
        row.prop(self, "power")
        
        
    @classmethod
    def poll(cls, context):
        a=0
        if context.active_object != None:
            if context.active_object.type == 'ARMATURE':
                if context.mode == 'EDIT_ARMATURE':
                    if len(context.selected_bones)>0:
                        a=1
        return a
    
    
    
    def execute(self, context):
        
        def adv_rename(string,insertname):
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
        
        def fib_recur(n):
            assert n >= 0, "n > 0"
            if n <= 1:
                return n
            return fib_recur(n-1) + fib_recur(n-2)
        f =[]
        num =self.number
        powNum =self.power
        for i in range(2, num+2):
            a=fib_recur(i)
            f.append(pow(a,powNum))

        #f1 =f[::-1]

        C = bpy.context
        o =C.object
        arm =C.object.data
        rootBone =C.selected_bones[0]
        rootBoneName=rootBone.name

        p =(rootBone.tail-rootBone.head)

        bones =[]
        for i,j in enumerate(f):
            boneName =adv_rename(rootBoneName,'_'+str(i))
            bone=arm.edit_bones.new(boneName)
            bone.roll =rootBone.roll
            bone.bbone_x = rootBone.bbone_x
            bone.bbone_z = rootBone.bbone_z
            if i==0:
                bone.head =rootBone.head
            else:
                bone.head =rootBone.head+p*(1-sum(f[:-i])/sum(f))
            bone.tail =rootBone.head+p*(1-sum(f[:-i-1])/sum(f))
            bones.append(bone)
            
        for i,j in enumerate(bones):
            if i>0:
                j.parent = bones[i-1]
                j.use_connect = True
                
        arm.edit_bones.remove(rootBone)
        
        bpy.ops.object.mode_set(mode='POSE')   
        
        bpy.ops.ed.undo_push(message="NB")
        return {'FINISHED'}


















classes=(
fibonacciBoneOperator,
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






