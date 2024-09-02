import bpy
import math 
import bmesh
import mathutils 


class NbLatticeAndBoneOperator(bpy.types.Operator):
    """晶格加控制器 选择晶格加选根骨骼"""
    bl_idname = "object.add_nblatticeandboneoperator"
    bl_label = "NB Lattice And Bone Ctrl"

    @classmethod
    def poll(cls, context):
        a=0
        MESH_s=[]
        LATTICE_s=[]
        ARMATURE_s=[]
       
        if context.mode == 'OBJECT':
            if len(context.selected_objects)>0:
                for i in bpy.context.selected_objects:
                    if i.type == 'LATTICE':
                        LATTICE_s.append(i)
                    if i.type == 'ARMATURE':
                        ARMATURE_s.append(i)    
        if len(LATTICE_s)==1 and len(ARMATURE_s)==1:
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
        
        MESH_s=[]

        for i in context.selected_objects:
            if i.type == 'LATTICE':
                Lattice = i
            if i.type == 'ARMATURE':
                ARMATURE= i
            if i.type == 'MESH':
                MESH_s.append(i)
                
        rootArm =ARMATURE
        rootBone =ARMATURE.data.bones.active
        rootBoneName=rootBone.name
        
        armName =Lattice.name+"_Arm"
        arm2Name =Lattice.name+"_Arm2"
        arm = bpy.data.armatures.new(armName)
        arm2 = bpy.data.armatures.new(arm2Name)
        o=bpy.data.objects.new(armName,arm)
        o2=bpy.data.objects.new(armName,arm2)
#        bpy.context.scene.collection.objects.link(o)
        rootArm.users_collection[0].objects.link(o)
        bpy.context.scene.collection.objects.link(o2)
          
        o.show_in_front = True
        bpy.context.view_layer.objects.active=o
        
        o.matrix_world=Lattice.matrix_world
        o2.matrix_world=Lattice.matrix_world
        
        cbsK=bpy.data.objects.new("NB",None)
        cbsK.empty_display_type = 'CUBE'
        
        
        pointNames=[]
        pointCo =[]
        for i,j in enumerate(Lattice.data.points):
            pointNames.append(adv_rename(Lattice.name,str(i)))
            pointCo.append(j.co)
            newBoneA_vertex_group = Lattice.vertex_groups.new(name=adv_rename(Lattice.name,str(i)))
            newBoneA_vertex_group.add([i], 1, 'REPLACE')
            
        modifier = Lattice.modifiers.new(name=Lattice.name+"ARMATURE", type='ARMATURE')
        modifier.object = o  
          
        bpy.ops.object.mode_set(mode='EDIT')
        for i,j in enumerate(pointNames):
            bone1 =arm.edit_bones.new(j)
            bone1.head =pointCo[i]
            bone1.tail =pointCo[i]+mathutils.Vector((0.0,-1.0,0.0))*(pointCo[0]-pointCo[1]).length*0.1
        
        bpy.ops.object.mode_set(mode='POSE')    
        for i,j in enumerate(pointNames):   
            o.pose.bones[j].custom_shape = cbsK
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_pattern(pattern=o.name,extend=False)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.mode_set(mode='POSE')
        

        bpy.context.view_layer.objects.active=o2
        
        bpy.ops.object.mode_set(mode='EDIT')
       
        for i,j in enumerate(pointNames):
            bone2 =arm2.edit_bones.new(adv_rename(j,"Ctrl"))
            bone2.head =pointCo[i]
            bone2.tail =pointCo[i]+mathutils.Vector((0.0,-1.0,0.0))*(pointCo[0]-pointCo[1]).length*0.05
            
        
        bpy.ops.object.mode_set(mode='POSE')    
        for i,j in enumerate(pointNames):   
            o2.pose.bones[adv_rename(j,"Ctrl")].custom_shape = cbsK
        

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_pattern(pattern=o2.name,extend=False)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

#        
        for i,j in enumerate(pointNames):
            ctCons =o.pose.bones[j].constraints.new('COPY_TRANSFORMS')
            ctCons.target = o2
            ctCons.subtarget = adv_rename(j,"Ctrl")


        bpy.context.view_layer.objects.active=rootArm
        bpy.ops.object.select_pattern(pattern=rootArm.name,extend=True)
        bpy.ops.object.join()

        bpy.ops.object.mode_set(mode='EDIT')
        for i,j in enumerate(pointNames):
            boneC =rootArm.data.edit_bones[adv_rename(j,"Ctrl")]
            boneC.tail =boneC.head+mathutils.Vector((0.0,-1.0,0.0))*(pointCo[0]-pointCo[1]).length*0.05
            boneC.parent = rootArm.data.edit_bones[rootBoneName]
        bpy.ops.object.mode_set(mode='OBJECT')   
            
        bpy.ops.object.select_pattern(pattern=o.name,extend=True)
        bpy.ops.object.select_pattern(pattern=Lattice.name,extend=True)
        bpy.ops.object.parent_set(type='BONE')
        
        
        o.hide_viewport = True
        o.hide_render = True

        bpy.ops.object.mode_set(mode='POSE') 

        if len(MESH_s)>0:
            for i in MESH_s:
                haslattice=0
                for j in i.modifiers[:]:
                    if j.type =='LATTICE':
                        if j.object==Lattice:
                            haslattice =1
                if haslattice==0: 
                    mod_lattice = i.modifiers.new(Lattice.name, 'LATTICE')
                    mod_lattice.object = Lattice
        bpy.ops.ed.undo_push(message="NB")
        return {'FINISHED'}   
    











classes=(
NbLatticeAndBoneOperator,
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






