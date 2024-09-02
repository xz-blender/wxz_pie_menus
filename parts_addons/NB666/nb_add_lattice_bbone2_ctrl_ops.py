import bpy
import math 
import bmesh
import mathutils 


class Nb2LatticeBoneOperator(bpy.types.Operator):
    """选择晶格加二段控制器"""
    bl_idname = "object.add_twolattice_bone_ctrl_operator"
    bl_label = "NB Two lattice Ctrl"

    @classmethod
    def poll(cls, context):
        a=0
        MESH_s=[]
        LATTICE_s=[]

        if context.mode == 'OBJECT':
            if len(context.selected_objects)>0:
                for i in bpy.context.selected_objects:
                    if i.type == 'LATTICE':
                        LATTICE_s.append(i)
        if len(LATTICE_s)==1:
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
            if i.type == 'MESH':
                MESH_s.append(i)
        
        C = bpy.context
        SelLattice =Lattice
        SelLattice.data.points_w = 16
        SelLattice.animation_data_clear()
        
        SelLattice.data.interpolation_type_u = 'KEY_LINEAR'
        SelLattice.data.interpolation_type_v = 'KEY_LINEAR'
        SelLattice.data.interpolation_type_w = 'KEY_LINEAR'
        SelLattice.lock_location[0] = True
        SelLattice.lock_location[1] = True
        SelLattice.lock_location[2] = True
        SelLattice.lock_rotation[0] = True
        SelLattice.lock_rotation[1] = True
        SelLattice.lock_rotation[2] = True
        SelLattice.lock_scale[0] = True
        SelLattice.lock_scale[1] = True
        SelLattice.lock_scale[2] = True

        armName =adv_rename(SelLattice.name,"_Arm")
        arm = bpy.data.armatures.new(armName)
        o=bpy.data.objects.new(armName,arm)
        bpy.context.scene.collection.objects.link(o)
        
        o.show_in_front = True
        bpy.context.view_layer.objects.active=o
        
        bpy.ops.object.mode_set(mode='EDIT')
        bone1Name =adv_rename(SelLattice.name,"_defbone")
        bone1 =arm.edit_bones.new(bone1Name)
        o.matrix_world=SelLattice.matrix_world
        

        bone1.head =(0.0, 0.0, -0.5)
        bone1.tail =(0.0, 0.0, 0.5)

        cbs=bpy.data.objects.new("NB",None)
        cbs.empty_display_type = 'SPHERE'
        
        cbsK=bpy.data.objects.new("NB",None)
        cbsK.empty_display_type = 'CUBE'
        
        arm.display_type = 'BBONE'
        bon_dir=(bone1.head-bone1.tail).normalized()
        bon_len=(bone1.head-bone1.tail).length
        
        boneAName =adv_rename(bone1.name,"bone_head")
        boneA =arm.edit_bones.new(boneAName)#下半截的骨骼
        try:
            boneA.layers[7] = True
            boneA.layers[1] = True
        except:
            pass
        boneA.head =bone1.head
        boneA.tail =bone1.tail-(bone1.tail-bone1.head)/2
        
        boneA.bbone_segments = 10
        
        boneBName =adv_rename(bone1.name,"bone_tail")
        boneB =arm.edit_bones.new(boneBName)#上半截的骨骼
        try:
            boneB.layers[7] = True
            boneB.layers[1] = True
        except:
            pass
        boneB.head =bone1.tail-(bone1.tail-bone1.head)/2
        boneB.tail =bone1.tail
        
        boneB.bbone_segments = 10
        
        boneB.parent=boneA
        boneB.use_connect = True
        
        boneTName =adv_rename(bone1.name,"boneT")
        boneT =arm.edit_bones.new(boneTName)#头部控制器骨骼
        try:
            boneT.layers[8] = True
            boneT.layers[1] = True
        except:
            pass
        boneT.head =bone1.tail
        boneT.tail =bone1.tail-bon_dir*bon_len*0.1
        boneT.use_deform = False
        
        boneHName =adv_rename(bone1.name,"boneH")
        boneH =arm.edit_bones.new(boneHName)#尾部控制器骨骼
        try:
            boneH.layers[8] = True
            boneH.layers[1] = True
        except:
            pass
        boneH.head =bone1.head
        boneH.tail =bone1.head-bon_dir*bon_len*0.1
        boneH.use_deform = False
        
        boneMPName =adv_rename(bone1.name,"boneMP")
        boneMP =arm.edit_bones.new(boneMPName)#中部记录位置的骨骼
        try:
            boneMP.layers[23] = True
        except:
            pass
        boneMP.head =bone1.tail-(bone1.tail-bone1.head)/2
        boneMP.tail =bone1.tail-(bone1.tail-bone1.head)/2-bon_dir*bon_len*0.1
        boneMP.use_deform = False
        
        boneMName =adv_rename(bone1.name,"boneM")
        boneM =arm.edit_bones.new(boneMName)#中部控制器骨骼
        try:
            boneM.layers[8] = True
            boneM.layers[1] = True
        except:
            pass
        boneM.head =bone1.tail-(bone1.tail-bone1.head)/2
        boneM.tail =bone1.tail-(bone1.tail-bone1.head)/2-bon_dir*bon_len*0.1
        boneM.use_deform = False
        boneM.parent = boneMP
        boneM.inherit_scale = 'NONE'
        
        boneA.bbone_custom_handle_start = boneH
        boneA.bbone_handle_type_start = 'TANGENT'
        boneA.bbone_custom_handle_end = boneM
        boneA.bbone_handle_type_end = 'TANGENT'
        boneA.bbone_segments = 15
        boneA.parent = boneH
        boneA.inherit_scale = 'NONE'
        
        boneB.bbone_custom_handle_start = boneM
        boneB.bbone_handle_type_start = 'TANGENT'
        boneB.bbone_custom_handle_end = boneT
        boneB.bbone_handle_type_end = 'TANGENT'
        boneB.bbone_segments = 15
        try:
            bone1.layers[23] = True
        except:
            pass
        bone1.use_deform = False
        bone1.bbone_custom_handle_start = boneH
        bone1.bbone_handle_type_start = 'TANGENT'
        bone1.bbone_custom_handle_end = boneT
        bone1.bbone_handle_type_end = 'TANGENT'
        bone1.bbone_segments = 30
        bone1.parent = boneH
        bone1.inherit_scale = 'NONE'
        
        boneMCCName =adv_rename(bone1.name,"boneMCC")
        boneMCC =arm.edit_bones.new(boneMCCName)#调曲率的骨骼
        try:
            boneMCC.layers[8] = True
            boneMCC.layers[1] = True
        except:
            pass
        boneMCC.head =bone1.tail-(bone1.tail-bone1.head)/2
        boneMCC.tail =bone1.tail-(bone1.tail-bone1.head)/2-bon_dir*bon_len*0.03
        boneMCC.use_deform = False
        boneMCC.parent = boneM
        
        boneA.bbone_z =boneA.bbone_x=bon_len*0.01
        boneB.bbone_z =boneB.bbone_x=bon_len*0.01
        boneT.bbone_z =boneT.bbone_x=bon_len*0.02
        boneH.bbone_z =boneH.bbone_x=bon_len*0.02
        boneM.bbone_z =boneM.bbone_x=bon_len*0.02
        boneMCC.bbone_z =boneMCC.bbone_x=bon_len*0.04
        boneMP.bbone_z =boneMP.bbone_x=bon_len*0.03
        boneMP.bbone_x*=0.1
        bone1.bbone_z =bone1.bbone_x=bon_len*0.01
        
        boneAname=boneA.name
        bone1name=bone1.name
        boneBname=boneB.name
        boneTname=boneT.name
        boneHname=boneH.name
        boneMPname=boneMP.name
        boneMname=boneM.name
        boneMCCname=boneMCC.name
        
        boneA.bbone_handle_use_scale_start[0] = True
        boneA.bbone_handle_use_scale_start[2] = True
        boneA.bbone_handle_use_scale_end[0] = True
        boneA.bbone_handle_use_scale_end[2] = True
        
        boneB.bbone_handle_use_scale_start[0] = True
        boneB.bbone_handle_use_scale_start[2] = True
        boneB.bbone_handle_use_scale_end[0] = True
        boneB.bbone_handle_use_scale_end[2] = True
        
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_pattern(pattern=o.name,extend=False)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.mode_set(mode='POSE')
        
                
        o.pose.bones[boneAname].lock_location[0] = True
        o.pose.bones[boneAname].lock_location[1] = True
        o.pose.bones[boneAname].lock_location[2] = True
        o.pose.bones[bone1name].lock_location[0] = True
        o.pose.bones[bone1name].lock_location[1] = True
        o.pose.bones[bone1name].lock_location[2] = True
        stConsA =o.pose.bones[boneAname].constraints.new('STRETCH_TO')
        stConsA.target = o
        stConsA.subtarget = boneMname
        #stConsA.rest_length = boneA.length
        stConsA.bulge = 1
     
        stConsB =o.pose.bones[boneBname].constraints.new('STRETCH_TO')
        stConsB.target = o
        stConsB.subtarget = boneTname
        #stConsB.rest_length = boneB.length
        stConsB.bulge = 0

        stConsZ =o.pose.bones[bone1name].constraints.new('STRETCH_TO')
        stConsZ.target = o
        stConsZ.subtarget = boneTname

        stConsMP =o.pose.bones[boneMPname].constraints.new('COPY_TRANSFORMS')
        stConsMP.target = o
        stConsMP.subtarget = bone1name
        stConsMP.head_tail = 0.5
        stConsMP.use_bbone_shape = True
        
        off =o.pose.bones[boneMname].head-boneM.head
        
        o.pose.bones[boneTname].custom_shape = cbs
        o.pose.bones[boneHname].custom_shape = cbs
        o.pose.bones[boneMname].custom_shape = cbs
        o.pose.bones[boneMCCname].custom_shape = cbsK
        o.pose.bones[boneMCCname].custom_shape_scale_xyz = (5,5,5)

        
#        bAsxDri=o.pose.bones[boneAname].driver_add("bbone_scaleinx")
#        varA1=bAsxDri.driver.variables.new()
#        varA1.targets[0].id=o
#        varA1.targets[0].data_path = "pose.bones[\""+boneHname+"\"].scale[0]"
#        bAsxDri.driver.expression="var"
#        
#        bAsyDri=o.pose.bones[boneAname].driver_add("bbone_scaleiny")
#        varA2=bAsyDri.driver.variables.new()
#        varA2.targets[0].id=o
#        varA2.targets[0].data_path = "pose.bones[\""+boneHname+"\"].scale[2]"
#        bAsyDri.driver.expression="var"

#        bAsxoDri=o.pose.bones[boneAname].driver_add("bbone_scaleoutx")
#        varA3=bAsxoDri.driver.variables.new()
#        varA3.targets[0].id=o
#        varA3.targets[0].data_path = "pose.bones[\""+boneMname+"\"].scale[0]"
#        bAsxoDri.driver.expression="var"
#        
#        bAsyoDri=o.pose.bones[boneAname].driver_add("bbone_scaleouty")
#        varA4=bAsyoDri.driver.variables.new()
#        varA4.targets[0].id=o
#        varA4.targets[0].data_path = "pose.bones[\""+boneMname+"\"].scale[2]"
#        bAsyoDri.driver.expression="var"

        
        
#        bBsxDri=o.pose.bones[boneBname].driver_add("bbone_scaleinx")
#        varB1=bBsxDri.driver.variables.new()
#        varB1.targets[0].id=o
#        varB1.targets[0].data_path = "pose.bones[\""+boneMname+"\"].scale[0]"
#        bBsxDri.driver.expression="var"
#        
#        bBsyDri=o.pose.bones[boneBname].driver_add("bbone_scaleiny")
#        varB2=bBsyDri.driver.variables.new()
#        varB2.targets[0].id=o
#        varB2.targets[0].data_path = "pose.bones[\""+boneMname+"\"].scale[2]"
#        bBsyDri.driver.expression="var"

#        bBsxoDri=o.pose.bones[boneBname].driver_add("bbone_scaleoutx")
#        varB3=bBsxoDri.driver.variables.new()
#        varB3.targets[0].id=o
#        varB3.targets[0].data_path = "pose.bones[\""+boneTname+"\"].scale[0]"
#        bBsxoDri.driver.expression="var"
#        
#        bBsyoDri=o.pose.bones[boneBname].driver_add("bbone_scaleouty")
#        varB4=bBsyoDri.driver.variables.new()
#        varB4.targets[0].id=o
#        varB4.targets[0].data_path = "pose.bones[\""+boneTname+"\"].scale[2]"
#        bBsyoDri.driver.expression="var"
#        
        o.pose.bones[boneBname].driver_remove("bbone_easein")
        bBeaseInDri=o.pose.bones[boneBname].driver_add("bbone_easein")
        varB5=bBeaseInDri.driver.variables.new()
        varB5.targets[0].id=o
        varB5.targets[0].data_path = "pose.bones[\""+boneMCCname+"\"].scale[2]"
        bBeaseInDri.driver.expression="(var-1)*2"
        
        o.pose.bones[boneAname].driver_remove("bbone_easeout")
        bAeaseInDri=o.pose.bones[boneAname].driver_add("bbone_easeout")
        varA5=bAeaseInDri.driver.variables.new()
        varA5.targets[0].id=o
        varA5.targets[0].data_path = "pose.bones[\""+boneMCCname+"\"].scale[0]"
        bAeaseInDri.driver.expression="(var-1)*2"
        
        stConsMCC =o.pose.bones[boneMCCname].constraints.new('LIMIT_SCALE')
        stConsMCC.use_min_x = True
        stConsMCC.use_min_y = True
        stConsMCC.use_min_z = True
        stConsMCC.use_max_x = True
        stConsMCC.use_max_y = True
        stConsMCC.use_max_z = True
        stConsMCC.min_x = 0.5
        stConsMCC.min_y = 0.5
        stConsMCC.min_z = 0.5
        stConsMCC.max_x = 1.5
        stConsMCC.max_y = 1.5
        stConsMCC.max_z = 1.5
        stConsMCC.use_transform_limit = True
        stConsMCC.owner_space = 'LOCAL'
        
        o.pose.bones[boneMCCname].lock_location[0] = True
        o.pose.bones[boneMCCname].lock_location[1] = True
        o.pose.bones[boneMCCname].lock_location[2] = True
        o.pose.bones[boneMCCname].lock_rotation_w = True
        o.pose.bones[boneMCCname].lock_rotation[0] = True
        o.pose.bones[boneMCCname].lock_rotation[1] = True
        o.pose.bones[boneMCCname].lock_rotation[2] = True
        
        
        newBoneA_vertex_group = SelLattice.vertex_groups.new(name=boneAName)
        vertex_group_data = range(len(SelLattice.data.points))
        for i in vertex_group_data:
            newBoneA_vertex_group.add([i], 1-i/len(SelLattice.data.points), 'REPLACE')

        
        newBoneB_vertex_group = SelLattice.vertex_groups.new(name=boneBName)
        vertex_group_data = range(len(SelLattice.data.points))
        for i in vertex_group_data:
            newBoneB_vertex_group.add([i], i/len(SelLattice.data.points), 'REPLACE')

            

        
        modifier = SelLattice.modifiers.new(name=SelLattice.name+"ARMATURE", type='ARMATURE')
        modifier.object = o
        modifier.use_deform_preserve_volume = True

        SelLattice.parent = o
        SelLattice.location[0] = 0
        SelLattice.location[1] = 0
        SelLattice.location[2] = 0
        SelLattice.rotation_euler[0] = 0
        SelLattice.rotation_euler[1] = 0
        SelLattice.rotation_euler[2] = 0
        SelLattice.rotation_quaternion[0] = 1
        SelLattice.rotation_quaternion[1] = 0
        SelLattice.rotation_quaternion[2] = 0
        SelLattice.rotation_quaternion[3] = 0

        if len(MESH_s)>0:
            for i in MESH_s:
                haslattice=0
                for j in i.modifiers[:]:
                    if j.type =='LATTICE':
                        if j.object==SelLattice:
                            haslattice =1
                if haslattice==0: 
                    mod_lattice = i.modifiers.new(SelLattice.name, 'LATTICE')
                    mod_lattice.object = SelLattice
                    
        bpy.ops.ed.undo_push(message="NB")
        return {'FINISHED'}



















classes=(
Nb2LatticeBoneOperator,
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






