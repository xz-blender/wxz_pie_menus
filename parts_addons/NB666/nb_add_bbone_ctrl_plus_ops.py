# coding=utf-8
import bpy
import math 
import bmesh
import mathutils 
import bmesh

class NbBbonePlusOperator(bpy.types.Operator):
    """add bbone ctrl ++"""
    bl_idname = "object.add_bbonectrlplusoperator"
    bl_label = "NB Bbone Ctrl +"

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
        
        mesh = bpy.data.meshes.new('CBS_Sphere')
        CBS_sphere = bpy.data.objects.new("Basic_Sphere", mesh)
        #bpy.context.collection.objects.link(basic_sphere)
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm,subdivisions=1, radius=1.0)
        bm.to_mesh(mesh)
        bm.free()
        
        selBoneName_s =[]
        childBoneName_s =[]
        parentBoneName_s =[]
        for i in C.selected_bones:
            selBoneName_s.append(i.name)

        
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.object.mode_set(mode='EDIT')
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
        
        for i in selBoneName_s:
            bone1=arm.edit_bones.get(i)
            if bone1.parent in C.selected_bones:
                if bone1.use_connect == True:
                    childBoneName_s.append(bone1.name)
                    parentBoneName_s.append(bone1.parent.name)

            
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
            
            bone_P_name =adv_rename(bone1.name,"_P")
            boneP =arm.edit_bones.new(bone_P_name)#头部新建个骨骼
            if bpy.app.version[0]==3:
                boneP.layers[8] = True
                boneP.layers[1] = True
                
            boneP.head =bone1.head
            boneP.tail =bone1.head-bon_dir*bon_len*0.2
            boneP.use_deform = False
            
            bone_t_name =adv_rename(bone1.name,"_t_Ctrl")
            bone1t =arm.edit_bones.new(bone_t_name)#尾部新建个骨骼
            if bpy.app.version[0]==3:
                bone1t.layers[8] = True
                bone1t.layers[1] = True

            bone1t.head =bone1.tail
            bone1t.tail =bone1.tail-bon_dir*bon_len*0.1
            bone1t.use_deform = False
            bone1t.parent = boneP


            bone_h_name =adv_rename(bone1.name,"_h_Ctrl")
            bone1h =arm.edit_bones.new(bone_h_name)#头部新建个骨骼
            if bpy.app.version[0]==3:
                bone1h.layers[8] = True
                bone1h.layers[1] = True
                
            bone1h.head =bone1.head
            bone1h.tail =bone1.head-bon_dir*bon_len*0.1
            bone1h.use_deform = False
            bone1h.parent = boneP


            bone_pole_name =adv_rename(bone1.name,"_pole")
            bone_pole =arm.edit_bones.new(bone_pole_name)#pole新建个骨骼
            if bpy.app.version[0]==3:
                bone_pole.layers[8] = True
                bone_pole.layers[1] = True

            bone_pole.head =(bone1.head+bone1.tail)/2
            bone_pole.tail =bone_pole.head-bon_dir*bon_len*0.1
            bone_pole.use_deform = False
            bone_pole.parent = boneP

            bone_pole_t_name =adv_rename(bone1.name,"_pole_t")
            bone_pole_t =arm.edit_bones.new(bone_pole_t_name)#pole新建个骨骼
            if bpy.app.version[0]==3:
                bone_pole_t.layers[8] = True
                bone_pole_t.layers[1] = True

            bone_pole_t.head =(bone1.head+bone1.tail)/2-bon_dir*bon_len*0.1
            bone_pole_t.tail =bone_pole_t.head-bon_dir*bon_len*0.06
            bone_pole_t.use_deform = False
            bone_pole_t.parent = bone_pole


            bone_pole_h_name =adv_rename(bone1.name,"_pole_h")
            bone_pole_h =arm.edit_bones.new(bone_pole_h_name)#pole新建个骨骼
            if bpy.app.version[0]==3:
                bone_pole_t.layers[8] = True
                bone_pole_t.layers[1] = True

            bone_pole_h.head =(bone1.head+bone1.tail)/2+bon_dir*bon_len*0.1
            bone_pole_h.tail =bone_pole_h.head-bon_dir*bon_len*0.06
            bone_pole_h.use_deform = False
            bone_pole_h.parent = bone_pole


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
            bone1.bbone_handle_use_scale_start[1] = True
            bone1.bbone_handle_use_scale_start[2] = True
            bone1.bbone_handle_use_scale_end[0] = True
            bone1.bbone_handle_use_scale_end[1] = True
            bone1.bbone_handle_use_scale_end[2] = True
            
            bone1t.roll=bone1.roll
            bone1h.roll=bone1.roll
            boneP.roll=bone1.roll
            bone_pole.roll=bone1.roll
            bone_pole_t.roll=bone1.roll
            bone_pole_h.roll=bone1.roll
            
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

            stCons =o.pose.bones.get(BN).constraints.new('COPY_SCALE')
            stCons.target = o
            stCons.subtarget = bone_P_name
            
            stCons =o.pose.bones.get(BN).constraints.new('STRETCH_TO')
            stCons.target = o
            stCons.subtarget = bone1tName

            stCons =o.pose.bones.get(bone_t_name).constraints.new('DAMPED_TRACK')
            stCons.target = o
            stCons.subtarget = bone_pole_t_name
            stCons.track_axis = 'TRACK_NEGATIVE_Y'

            stCons =o.pose.bones.get(bone_h_name).constraints.new('DAMPED_TRACK')
            stCons.target = o
            stCons.subtarget = bone_pole_h_name
            
            o.pose.bones[bone_pole_name]["scale handle"]=1.0
            o.pose.bones[bone_pole_name].id_properties_ui("scale handle").update(min=0.0,max=1.0)

            stCons =o.pose.bones.get(bone_t_name).constraints.new('TRANSFORM')
            stCons.target = o
            stCons.subtarget = bone_pole_name
            stCons.target_space = 'LOCAL'
            stCons.owner_space = 'LOCAL'
            stCons.from_min_y = -0.5*bon_len
            stCons.from_max_y = 0.5*bon_len
            stCons.map_to = 'SCALE'
            stCons.to_min_y_scale = 1.9
            stCons.to_max_y_scale = 0.1
            stCons.mix_mode_scale = 'MULTIPLY'
            
            stCons.driver_remove("influence")
            fc =stCons.driver_add("influence")

            var1 = fc.driver.variables.new()
            var1.name = "v"
            var1.targets[0].id=o
        #    var1.type = 'SINGLE_PROP'
            var1.targets[0].data_path = 'pose.bones["'+bone_pole_name+'"]["scale handle"]'   
            fc.driver.expression ="v"
            
            
            stCons =o.pose.bones.get(bone_h_name).constraints.new('TRANSFORM')
            stCons.target = o
            stCons.subtarget = bone_pole_name
            stCons.target_space = 'LOCAL'
            stCons.owner_space = 'LOCAL'
            stCons.from_min_y = -0.5*bon_len
            stCons.from_max_y = 0.5*bon_len
            stCons.map_to = 'SCALE'
            stCons.to_min_y_scale = 0.1
            stCons.to_max_y_scale = 1.9
            stCons.mix_mode_scale = 'MULTIPLY'

            stCons.driver_remove("influence")
            fc =stCons.driver_add("influence")

            var1 = fc.driver.variables.new()
            var1.name = "v"
            var1.targets[0].id=o
        #    var1.type = 'SINGLE_PROP'
            var1.targets[0].data_path = 'pose.bones["'+bone_pole_name+'"]["scale handle"]'   
            fc.driver.expression ="v"
            

            o.pose.bones[i].driver_remove("bbone_easein")
            fc =o.pose.bones[i].driver_add("bbone_easein")
            var1 = fc.driver.variables.new()
            var1.name = "v"
            var1.targets[0].id=o
        #    var1.type = 'SINGLE_PROP'
            var1.targets[0].data_path = 'pose.bones["'+bone_pole_t_name+'"]location[1]'   
            fc.driver.expression ="v/"+str(bon_len)

            o.pose.bones[i].driver_remove("bbone_easeout")
            fc =o.pose.bones[i].driver_add("bbone_easeout")
            var1 = fc.driver.variables.new()
            var1.name = "v"
            var1.targets[0].id=o
        #    var1.type = 'SINGLE_PROP'
            var1.targets[0].data_path = 'pose.bones["'+bone_pole_h_name+'"]location[1]'   
            fc.driver.expression ="-v/"+str(bon_len)
            

            
            o.pose.bones.get(bone1tName).custom_shape = cbs
            o.pose.bones.get(bone1hName).custom_shape = cbs
            o.pose.bones.get(bone_P_name).custom_shape = cbs
            o.pose.bones.get(bone_pole_name).custom_shape = CBS_sphere
            o.pose.bones.get(bone_pole_t_name).custom_shape = CBS_sphere
            o.pose.bones.get(bone_pole_h_name).custom_shape = CBS_sphere
            bpy.ops.object.mode_set(mode='EDIT')

       
            
        bpy.ops.object.mode_set(mode='POSE')
        
        bpy.ops.ed.undo_push(message="NB")
        return {'FINISHED'}



















classes=(
NbBbonePlusOperator,
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






