# coding=utf-8
import bpy
import math 
import bmesh
import mathutils 


class NbBboneOperator(bpy.types.Operator):
    """add bbone ctrl"""
    bl_idname = "object.add_bbonectrloperator"
    bl_label = "NB Bbone Ctrl"

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
#        bone1 =C.selected_bones[0]#获取选择骨骼
        
        arm.display_type = 'BBONE'
        
        cbs=bpy.data.objects.new("NB",None)
        cbs.empty_display_type = 'SPHERE'
        
        selBoneName_s =[]
        childBoneName_s =[]
        parentBoneName_s =[]
        chainrootBoneName_s =[]
        chaintailBoneName_s =[]
        chainroot_child_BoneName_s =[]
        chaintail_parent_BoneName_s =[]
        
        
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.object.mode_set(mode='EDIT')
        
        for i in C.selected_bones:
            selBoneName_s.append(i.name)

        
        
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
                
#           if any(string.lower().startswith(prefix) for prefix in prefixes):
#                # 找到前缀的位置
#                prefix_index = 0
#                for prefix in prefixes:
#                    if string.lower().startswith(prefix):
#                        prefix_index += len(prefix)
#                        break
#                # 在前缀后插入"_ddd"
#                newName = string[:prefix_index] + insertname + string[prefix_index:]
#                
            else:
                newName=string+ insertname 
            return newName
        
        
        def reflect_vector(vector_V, vector_N):
            vector_V = vector_V
            vector_N = vector_N
            vector_N.normalize()  # 确保N是单位向量
            reflection_result = vector_V - 2 * vector_V.dot(vector_N) * vector_N
            return reflection_result
        
        # 获取骨骼的方向向量的函数
        def get_bone_direction(bone):
            # 骨骼方向通过头部到尾部的向量计算
            direction = bone.tail - bone.head
            return direction.normalized()
        
        
        for i in selBoneName_s:
            bone1=arm.edit_bones.get(i)
            if bone1.parent in C.selected_bones:
                if bone1.use_connect == True:
                    childBoneName_s.append(bone1.name)
                    parentBoneName_s.append(bone1.parent.name)
                    if bone1.parent.use_connect == False:
                        chainrootBoneName_s.append(bone1.parent.name)
                    is_zuihou =True
                    for b in bone1.children[:]:
                        if b.use_connect:
                            is_zuihou =False  
                    if is_zuihou:
                        chaintailBoneName_s.append(bone1.name)
                      
#        print(chainrootBoneName_s)
#        print(chaintailBoneName_s)
            
        for i in chainrootBoneName_s:
            bone1=arm.edit_bones.get(i)
            chainroot_child_BoneName_s.append(bone1.children[0].name)
            
        for i in chaintailBoneName_s:
            bone1=arm.edit_bones.get(i)
            chaintail_parent_BoneName_s.append(bone1.parent.name)
            
            
        for i in selBoneName_s:
            bone1=arm.edit_bones.get(i)
            
            if bpy.app.version[0]==3:
                bone1.layers[7] = True
                bone1.layers[1] = True
                
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


            
            bon_dir=(bone1.head-bone1.tail).normalized()
            bon_len=(bone1.head-bone1.tail).length
            

            bone_t_name =adv_rename(bone1.name,"_t_Ctrl")
            bone1t =arm.edit_bones.new(bone_t_name)#尾部新建个骨骼
            if bpy.app.version[0]==3:
                bone1t.layers[8] = True
                bone1t.layers[1] = True

            bone1t.head =bone1.tail
            bone1t.tail =bone1.tail-bon_dir*bon_len*0.1
            bone1t.use_deform = False


            bone_h_name =adv_rename(bone1.name,"_h_Ctrl")
            bone1h =arm.edit_bones.new(bone_h_name)#头部新建个骨骼
            bone1h.parent = bone1.parent
            if bpy.app.version[0]==3:
                bone1h.layers[8] = True
                bone1h.layers[1] = True

            bone1h.head =bone1.head
            bone1h.tail =bone1.head-bon_dir*bon_len*0.1
            bone1h.use_deform = False

            bone1.bbone_custom_handle_start = bone1h
            bone1.bbone_handle_type_start ='TANGENT'
            bone1.bbone_custom_handle_end = bone1t
            bone1.bbone_handle_type_end = 'TANGENT'
            bone1.use_connect = False
            bone1.parent = bone1h
            
            bone1.inherit_scale = 'NONE'
            bone1.bbone_segments = 16
            bone1.bbone_z =bone1.bbone_x=bon_len*0.01
            bone1t.bbone_z =bone1t.bbone_x=bon_len*0.02
            bone1h.bbone_z =bone1h.bbone_x=bon_len*0.02
            bone1.bbone_z*=2
            
            bone1.bbone_handle_use_scale_start[0] = True
            bone1.bbone_handle_use_scale_start[2] = True
            bone1.bbone_handle_use_scale_end[0] = True
            bone1.bbone_handle_use_scale_end[2] = True
            
            bone1t.roll=bone1.roll
            bone1h.roll=bone1.roll
            
            BN =bone1.name
            bone1tName =bone1t.name
            bone1hName =bone1h.name
            bpy.ops.object.mode_set(mode='POSE')
            
            o.pose.bones.get(BN).location[0] = 0
            o.pose.bones.get(BN).location[1] = 0
            o.pose.bones.get(BN).location[2] = 0
            o.pose.bones.get(BN).scale[0] = 1
            o.pose.bones.get(BN).scale[1] = 1
            o.pose.bones.get(BN).scale[2] = 1
            o.pose.bones.get(BN).lock_location[0] = True
            o.pose.bones.get(BN).lock_location[1] = True
            o.pose.bones.get(BN).lock_location[2] = True
            
            stCons =o.pose.bones.get(BN).constraints.new('STRETCH_TO')
            stCons.target = o
            stCons.subtarget = bone1tName
            
            o.pose.bones.get(bone1tName).custom_shape = cbs
            o.pose.bones.get(bone1hName).custom_shape = cbs
            bpy.ops.object.mode_set(mode='EDIT')


        All_bbone_z_s=[]
        All_bbone_x_s=[]
        All_ctrl_bbone_z_s=[]
        All_ctrl_length_s=[]
        for i,b in enumerate(childBoneName_s):
            bone1=arm.edit_bones.get(b)
            boneh=arm.edit_bones.get(adv_rename(parentBoneName_s[i],"_t_Ctrl"))
            bone1.bbone_custom_handle_start = boneh
            bone1.parent = boneh
            
            arm.edit_bones.remove(arm.edit_bones.get(adv_rename(b,"_h_Ctrl")))
            
            
            bone2 = arm.edit_bones.get(parentBoneName_s[i])

            # 计算方向向量
            dir1 = get_bone_direction(bone1)
            dir2 = get_bone_direction(bone2)

            # 计算平均方向
            average_direction = (dir1 + dir2) / 2.0

            # 归一化平均方向
            average_direction.normalize()
            

            # 将目标骨骼的方向设置为平均方向
            # 可以通过将目标骨骼的尾部对齐到新的方向来实现
            boneh.tail = boneh.head + average_direction*boneh.length
            boneh.align_roll((bone1.z_axis+bone2.z_axis)/2)
            
            All_bbone_z_s.append(bone1.bbone_z)
            All_bbone_x_s.append(bone1.bbone_x)
            All_ctrl_bbone_z_s.append(boneh.bbone_z)
            All_ctrl_length_s.append(boneh.length)
            
        for i,b in enumerate(childBoneName_s):
            bone1=arm.edit_bones.get(b)
            bone2 = arm.edit_bones.get(parentBoneName_s[i])
            bonet=arm.edit_bones.get(adv_rename(b,"_t_Ctrl"))
            
            bone1.bbone_z =sum(All_bbone_z_s)/len(All_bbone_z_s)
            bone2.bbone_z =sum(All_bbone_z_s)/len(All_bbone_z_s)
            bone1.bbone_x =sum(All_bbone_x_s)/len(All_bbone_x_s)
            bone2.bbone_x =sum(All_bbone_x_s)/len(All_bbone_x_s)
            bonet.bbone_z =bonet.bbone_x=sum(All_ctrl_bbone_z_s)/len(All_ctrl_bbone_z_s)
            bonet.length =sum(All_ctrl_length_s)/len(All_ctrl_length_s)
        
        
#        if childBoneName_s:
#            bone_zuihou=arm.edit_bones.get(adv_rename(childBoneName_s[-1],"_t_Ctrl"))
#            bone1 = arm.edit_bones.get(childBoneName_s[-1])
#            bone2 = arm.edit_bones.get(parentBoneName_s[-1])
#            dir1 = get_bone_direction(bone1)
#            dir2 = get_bone_direction(bone2)
#            average_direction = (dir1 + dir2) / 2.0
#            average_direction.normalize()
#            ref_direction=reflect_vector(-average_direction,dir1)
#            bone_zuihou.tail = bone_zuihou.head + ref_direction*boneh.length
#            bone_zuihou.align_roll((bone1.z_axis+bone2.z_axis)/2)
#        
#            bone_zuiqian=arm.edit_bones.get(adv_rename(parentBoneName_s[0],"_h_Ctrl"))
#            bone2 = arm.edit_bones.get(childBoneName_s[0])
#            bone1 = arm.edit_bones.get(parentBoneName_s[0])
#            dir1 = get_bone_direction(bone1)
#            dir2 = get_bone_direction(bone2)
#            average_direction = (dir1 + dir2) / 2.0
#            average_direction.normalize()
#            ref_direction=reflect_vector(-average_direction,dir1)
#            bone_zuiqian.tail = bone_zuiqian.head + ref_direction*boneh.length
#            bone_zuiqian.align_roll((bone1.z_axis+bone2.z_axis)/2)
            
        for i,b in enumerate(chaintailBoneName_s):
            bone_zuihou=arm.edit_bones.get(adv_rename(b,"_t_Ctrl"))
            bone1 = arm.edit_bones.get(b)
            bone2 = arm.edit_bones.get(chaintail_parent_BoneName_s[i])
            dir1 = get_bone_direction(bone1)
            dir2 = get_bone_direction(bone2)
            average_direction = (dir1 + dir2) / 2.0
            average_direction.normalize()
            ref_direction=reflect_vector(-average_direction,dir1)
            bone_zuihou.tail = bone_zuihou.head + ref_direction*boneh.length
            bone_zuihou.align_roll((bone1.z_axis+bone2.z_axis)/2)
            
        for i,b in enumerate(chainrootBoneName_s):
            bone_zuiqian=arm.edit_bones.get(adv_rename(b,"_h_Ctrl"))
            chainroot_child_BoneName_s
            bone2 = arm.edit_bones.get(chainroot_child_BoneName_s[i])
            bone1 = arm.edit_bones.get(b)
            dir1 = get_bone_direction(bone1)
            dir2 = get_bone_direction(bone2)
            average_direction = (dir1 + dir2) / 2.0
            average_direction.normalize()
            ref_direction=reflect_vector(-average_direction,dir1)
            bone_zuiqian.tail = bone_zuiqian.head + ref_direction*boneh.length
            bone_zuiqian.align_roll((bone1.z_axis+bone2.z_axis)/2)                
            arm.edit_bones.get(adv_rename(b,"_t_Ctrl")).length =sum(All_ctrl_length_s)/len(All_ctrl_length_s)
            
            
        bpy.ops.object.mode_set(mode='POSE')
        
        bpy.ops.ed.undo_push(message="NB")
        return {'FINISHED'}



















classes=(
NbBboneOperator,
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






