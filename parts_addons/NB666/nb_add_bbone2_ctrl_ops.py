import bpy
import math 
import bmesh
import mathutils 


class Nb2BboneOperator(bpy.types.Operator):
    """选择骨骼添加二段控制器"""
    bl_idname = "object.add_twobbonectrloperator"
    bl_label = "NB Tow Bbone Ctrl"

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
        C = bpy.context
        o =C.object
        arm =C.object.data
        bone1 =C.selected_bones[0]#获取选择骨骼
        
        cbs=bpy.data.objects.new("NB",None)
        cbs.empty_display_type = 'SPHERE'
        cbsK=bpy.data.objects.new("NB",None)
        cbsK.empty_display_type = 'CUBE'
        
        arm.display_type = 'BBONE'
        selBoneName_s =[]
        for i in C.selected_bones:
            selBoneName_s.append(i.name)
            i.use_connect = False

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.object.mode_set(mode='EDIT')
        
        def adv_rename(string,insertname):
#           prefixes = ["left", "right", "l_", "r_", "l.", "r.", "l-", "r-", "l ", "r "]
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
                
#           if any(string.lower().startswith(prefix) for prefix in prefixes):
#                # 找到前缀的位置
#                prefix_index = 0
#                for prefix in prefixes:
#                    if string.lower().startswith(prefix):
#                        prefix_index += len(prefix)
#                        break
#                # 在前缀后插入"_ddd"
#                newName = string[:prefix_index] + insertname + string[prefix_index:]
                
            else:
                newName=string+ insertname 
            return newName
        
        for i in selBoneName_s:
            
            o.pose.bones[i].driver_remove("bbone_scalein",0)
            o.pose.bones[i].driver_remove("bbone_scalein",1)
            o.pose.bones[i].driver_remove("bbone_scalein",2)
            o.pose.bones[i].driver_remove("bbone_scaleout",0)
            o.pose.bones[i].driver_remove("bbone_scaleout",1)
            o.pose.bones[i].driver_remove("bbone_scaleout",2)
            o.pose.bones[i].driver_remove("bbone_easein")
            o.pose.bones[i].driver_remove("bbone_easeout")
            
            o.pose.bones[i].bbone_scalein[0] = 1
            o.pose.bones[i].bbone_scalein[1] = 1
            o.pose.bones[i].bbone_scalein[2] = 1
            o.pose.bones[i].bbone_scaleout[0] = 1
            o.pose.bones[i].bbone_scaleout[1] = 1
            o.pose.bones[i].bbone_scaleout[2] = 1
            o.pose.bones[i].bbone_easein = 0
            o.pose.bones[i].bbone_easeout = 0
            
            bone1=arm.edit_bones.get(i)
            
            bon_dir=(bone1.head-bone1.tail).normalized()
            bon_len=(bone1.head-bone1.tail).length
            
            boneAName =adv_rename(bone1.name,"bone_head")
            boneA =arm.edit_bones.new(boneAName)#下半截的骨骼
            if bpy.app.version[0]==3:
                boneA.layers[7] = True
                boneA.layers[1] = True

            boneA.head =bone1.head
            boneA.tail =bone1.tail-(bone1.tail-bone1.head)/2
            boneA.roll =bone1.roll
            boneA.bbone_segments = 10
            
            boneBName =adv_rename(bone1.name,"bone_tail")
            boneB =arm.edit_bones.new(boneBName)#上半截的骨骼
            if bpy.app.version[0]==3:
                boneB.layers[7] = True
                boneB.layers[1] = True

            boneB.head =bone1.tail-(bone1.tail-bone1.head)/2
            boneB.tail =bone1.tail
            boneB.roll=bone1.roll
            boneB.bbone_segments = 10
            
            boneB.parent=boneA
            boneB.use_connect = True
            
            boneTName =adv_rename(bone1.name,"boneT")
            boneT =arm.edit_bones.new(boneTName)#头部控制器骨骼
            if bpy.app.version[0]==3:
                boneT.layers[8] = True
                boneT.layers[1] = True

            boneT.head =bone1.tail
            boneT.tail =bone1.tail-bon_dir*bon_len*0.1
            boneT.roll=bone1.roll
            boneT.use_deform = False
            
            boneHName =adv_rename(bone1.name,"boneH")
            boneH =arm.edit_bones.new(boneHName)#尾部控制器骨骼
            if bpy.app.version[0]==3:
                boneH.layers[8] = True
                boneH.layers[1] = True

            boneH.head =bone1.head
            boneH.tail =bone1.head-bon_dir*bon_len*0.1
            boneH.roll=bone1.roll
            boneH.use_deform = False
            
            boneMPName =adv_rename(bone1.name,"boneMP")
            boneMP =arm.edit_bones.new(boneMPName)#中部记录位置的骨骼
            if bpy.app.version[0]==3:
                boneMP.layers[23] = True

            boneMP.head =bone1.tail-(bone1.tail-bone1.head)/2
            boneMP.tail =bone1.tail-(bone1.tail-bone1.head)/2-bon_dir*bon_len*0.1
            boneMP.roll=bone1.roll
            boneMP.use_deform = False
            
            boneMName =adv_rename(bone1.name,"boneM")
            boneM =arm.edit_bones.new(boneMName)#中部控制器骨骼
            if bpy.app.version[0]==3:
                boneM.layers[8] = True
                boneM.layers[1] = True

            boneM.head =bone1.tail-(bone1.tail-bone1.head)/2
            boneM.tail =bone1.tail-(bone1.tail-bone1.head)/2-bon_dir*bon_len*0.1
            boneM.roll=bone1.roll
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

            boneZ =bone1
            if bpy.app.version[0]==3:
                boneZ.layers[23] = True
            boneZ.roll=bone1.roll
            boneZ.use_deform = False
            boneZ.bbone_custom_handle_start = boneH
            boneZ.bbone_handle_type_start = 'TANGENT'
            boneZ.bbone_custom_handle_end = boneT
            boneZ.bbone_handle_type_end = 'TANGENT'
            boneZ.bbone_segments = 30
            boneZ.parent = boneH
            boneZ.inherit_scale = 'NONE'
            
            boneMCCName =adv_rename(bone1.name,"boneMCC")
            boneMCC =arm.edit_bones.new(boneMCCName)#调曲率的骨骼
            if bpy.app.version[0]==3:
                boneMCC.layers[8] = True
                boneMCC.layers[1] = True

            boneMCC.head =bone1.tail-(bone1.tail-bone1.head)/2
            boneMCC.tail =bone1.tail-(bone1.tail-bone1.head)/2-bon_dir*bon_len*0.03
            boneMCC.roll=bone1.roll
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
            boneZ.bbone_z =boneZ.bbone_x=bon_len*0.01
            
            boneAname=boneA.name
            boneBname=boneB.name
            boneZname=boneZ.name
            boneMPname=boneMP.name
            boneTname=boneT.name
            boneHname=boneH.name
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
            
            
            
            
            bpy.ops.object.mode_set(mode='POSE')
                    
            o.pose.bones[boneAname].lock_location[0] = True
            o.pose.bones[boneAname].lock_location[1] = True
            o.pose.bones[boneAname].lock_location[2] = True
            o.pose.bones[boneZname].lock_location[0] = True
            o.pose.bones[boneZname].lock_location[1] = True
            o.pose.bones[boneZname].lock_location[2] = True
            stConsA =o.pose.bones[boneAname].constraints.new('STRETCH_TO')
            stConsA.target = o
            stConsA.subtarget = boneMname
    #        stConsA.rest_length = boneA.length
            stConsA.bulge = 1
         
            stConsB =o.pose.bones[boneBname].constraints.new('STRETCH_TO')
            stConsB.target = o
            stConsB.subtarget = boneTname
    #        stConsB.rest_length = boneB.length
            stConsB.bulge = 0

            stConsZ =o.pose.bones[boneZname].constraints.new('STRETCH_TO')
            stConsZ.target = o
            stConsZ.subtarget = boneTname

            stConsMP =o.pose.bones[boneMPname].constraints.new('COPY_TRANSFORMS')
            stConsMP.target = o
            stConsMP.subtarget = boneZname
            stConsMP.head_tail = 0.5
            stConsMP.use_bbone_shape = True
            
            off =o.pose.bones[boneMname].head-boneM.head
            
            o.pose.bones[boneTname].custom_shape = cbs
            o.pose.bones[boneHname].custom_shape = cbs
            o.pose.bones[boneMname].custom_shape = cbs
            o.pose.bones[boneMCCname].custom_shape = cbsK
            o.pose.bones[boneMCCname].custom_shape_scale_xyz = (5,5,5)

            

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
            bpy.ops.object.mode_set(mode='EDIT')

        bpy.ops.object.mode_set(mode='POSE')


        bpy.ops.ed.undo_push(message="NB")
        return {'FINISHED'}














classes=(
Nb2BboneOperator,
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






