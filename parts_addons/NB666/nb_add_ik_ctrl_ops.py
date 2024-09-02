import bpy
import math 
import bmesh
import mathutils 


class NbIKBoneOperator(bpy.types.Operator):
    """编辑模式选择骨骼链末端骨骼 循环添加IK控制"""
    bl_idname = "object.add_nbikboneoperator"
    bl_label = "NB IK Bbone Ctrl"

    @classmethod
    def poll(cls, context):
        a=0
        if context.active_object != None:
            if context.active_object.type == 'ARMATURE':
                if context.mode == 'EDIT_ARMATURE':
                    if len(context.selected_bones)>0:
                        if len(context.selected_bones[0].parent_recursive)>0:
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
        
        lensum =0
        for i in bone1.parent_recursive:
            lensum+=(i.head-i.tail).length
            
        bon_len=lensum/len(bone1.parent_recursive)
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
        
        def nb_ik(Abone,needBoneC =None,needBonet=None,needBonej=None):
            
            try:
                Abone.layers[1] = True
            except:
                pass
            
            Abone.bbone_segments = 15
            Abone.inherit_scale = 'NONE'            
            
            bonetName =adv_rename(Abone.name,"ctrl_t")
            bonet =arm.edit_bones.new(bonetName)#尾部新建个骨骼
            try:
                bonet.layers[8] = True
                bonet.layers[1] = True
            except:
                pass
            bonet.head =Abone.tail
            bonet.tail =Abone.tail+mathutils.Vector((0.0,-1.0,0.0))*bon_len*0.2
            bonet.use_deform = False
            bonet.use_inherit_rotation = False
            bonet.inherit_scale = 'NONE'
            bonet.roll =Abone.roll

            bonejName =adv_rename(Abone.name,"ctrl_j")
            bonej =arm.edit_bones.new(bonejName)#尾部新建个骨骼
            try:
                bonej.layers[8] = True
                bonej.layers[1] = True
            except:
                pass
            bonej.head =Abone.tail
            bonej.tail =Abone.tail+mathutils.Vector((0.0,-1.0,0.0))*bon_len*0.2
            bonej.use_deform = False
            bonej.use_inherit_rotation = False
            bonej.parent =bonet
            bonej.roll =Abone.roll

            
            boneCName =adv_rename(Abone.name,"copy_C")
            boneC =arm.edit_bones.new(boneCName)#原位置新建个骨骼
            try:
                boneC.layers[23] = True
            except:
                pass
            boneC.head =Abone.head
            boneC.tail =Abone.tail
            boneC.use_deform = False
            boneC.use_connect = True
            boneC.roll =Abone.roll
            
            if len(Abone.children)>0:
                bonet.parent=boneC
            
            bonet.bbone_z =bonet.bbone_x=bon_len*0.1
            
                
            needBoneC=boneC
            needBonet=bonet
            needBonej=bonej
            return needBoneC,needBonet,needBonej


        def nb_ikk(Abone,boneCs =[],bonets=[],abones =[],bonejs=[]):   #递归骨骼链
            r=nb_ik(Abone)
            needBoneC =r[0]
            boneCs.append(needBoneC)
            bonets.append(r[1])
            abones.append(Abone)
            bonejs.append(r[2])
            if Abone.parent !=None: 
                if Abone.use_connect:
                    Abone=Abone.parent  
                    nb_ikk(Abone)
            return boneCs,bonets,abones,bonejs
                
        
        
        
        r=nb_ikk(bone1)
        boneCs=r[0]
#        print(boneCs)
        for i,b in enumerate(boneCs):
            
#            print(b.name)
#            print(i)
            if i+1<len(boneCs):
                b.parent =boneCs[i+1]
            
        bonets=r[1]
        abones=r[2]
        bonejs=r[3]
        
        rootboneName =adv_rename(abones[-1].name,"ctrl_root")
        rootbone =arm.edit_bones.new(rootboneName)#尾部新建个骨骼
        try:
            rootbone.layers[8] = True
            rootbone.layers[1] = True
        except:
            pass
        rootbone.head =abones[-1].head
        rootbone.tail =abones[-1].head+mathutils.Vector((0.0,-1.0,0.0))*bon_len*0.2
        rootbone.use_deform = False
        rootbone.use_inherit_rotation = False
        
        abones[-1].parent =rootbone
        boneCs[-1].use_connect = False
        boneCs[-1].parent =rootbone
        
        
        boneCs=[]
        for i in r[0]:
            boneCs.append(i.name)
        
        bonets=[]
        for i in r[1]:
            bonets.append(i.name)
            
        abones=[]
        for i in r[2]:
            abones.append(i.name)
            
        bonejs=[]
        for i in r[3]:
            bonejs.append(i.name)
        
        
        bpy.ops.object.mode_set(mode='POSE')


        o.pose.bones[rootboneName].custom_shape = cbs
        for i,b in enumerate(bonets):
#            print(b.name)
#            print(i)
            dampCons =o.pose.bones[abones[i]].constraints.new('DAMPED_TRACK')
            dampCons.target = o
            dampCons.subtarget = b
            stCons =o.pose.bones[abones[i]].constraints.new('STRETCH_TO')
            stCons.target = o
            stCons.subtarget = b      

            o.pose.bones[boneCs[i]].ik_stretch = 0.01
            
            o.pose.bones[bonets[i]].custom_shape = cbs
            o.pose.bones[bonejs[i]].custom_shape = cbsK
            
            o.pose.bones[abones[i]].driver_remove("bbone_scaleout",0)
            sxDri=o.pose.bones[abones[i]].driver_add("bbone_scaleout",0)
            var1=sxDri.driver.variables.new()
            var1.targets[0].id=o
            var1.targets[0].data_path = "pose.bones[\""+b+"\"].scale[0]"
            sxDri.driver.expression="var"
            
            o.pose.bones[abones[i]].driver_remove("bbone_scaleout",2)
            syDri=o.pose.bones[abones[i]].driver_add("bbone_scaleout",2)
            var1=syDri.driver.variables.new()
            var1.targets[0].id=o
            var1.targets[0].data_path = "pose.bones[\""+b+"\"].scale[2]"
            syDri.driver.expression="var"
           
            o.pose.bones[abones[i]].driver_remove("bbone_easeout")
            easeoutDri=o.pose.bones[abones[i]].driver_add("bbone_easeout")
            var1=easeoutDri.driver.variables.new()
            var1.targets[0].id=o
            var1.targets[0].data_path = "pose.bones[\""+bonejs[i]+"\"].scale[0]"
            easeoutDri.driver.expression="(var-1)*2"
                
            stConsMCC =o.pose.bones[bonejs[i]].constraints.new('LIMIT_SCALE')
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
            o.pose.bones[bonejs[i]].lock_location[0] = True
            o.pose.bones[bonejs[i]].lock_location[1] = True
            o.pose.bones[bonejs[i]].lock_location[2] = True
            o.pose.bones[bonejs[i]].lock_rotation_w = True
            o.pose.bones[bonejs[i]].lock_rotation[0] = True
            o.pose.bones[bonejs[i]].lock_rotation[1] = True
            o.pose.bones[bonejs[i]].lock_rotation[2] = True
            
            
            
            
            if i+1<len(bonets):
                o.pose.bones[abones[i]].driver_remove("bbone_scalein",0)
                sxiDri=o.pose.bones[abones[i]].driver_add("bbone_scalein",0)
                var1=sxiDri.driver.variables.new()
                var1.targets[0].id=o
                var1.targets[0].data_path = "pose.bones[\""+bonets[i+1]+"\"].scale[0]"
                sxiDri.driver.expression="var"
                
                o.pose.bones[abones[i]].driver_remove("bbone_scalein",2)
                syiDri=o.pose.bones[abones[i]].driver_add("bbone_scalein",2)
                var1=syiDri.driver.variables.new()
                var1.targets[0].id=o
                var1.targets[0].data_path = "pose.bones[\""+bonets[i+1]+"\"].scale[2]"
                syiDri.driver.expression="var"
                
                o.pose.bones[abones[i]].driver_remove("bbone_easein")
                easeinDri=o.pose.bones[abones[i]].driver_add("bbone_easein")
                var1=easeinDri.driver.variables.new()
                var1.targets[0].id=o
                var1.targets[0].data_path = "pose.bones[\""+bonejs[i+1]+"\"].scale[2]"
                easeinDri.driver.expression="(var-1)*2"
            
        ikCons =o.pose.bones[boneCs[0]].constraints.new('IK')
        ikCons.target = o
        ikCons.subtarget = bonets[0]       
        ikCons.chain_count =len(bonets)


        bpy.ops.ed.undo_push(message="NB")
        return {'FINISHED'}
    











classes=(
NbIKBoneOperator,
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






