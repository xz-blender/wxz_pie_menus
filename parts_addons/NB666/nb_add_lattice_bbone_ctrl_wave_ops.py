# coding=utf-8
import bpy
import math 
import bmesh
import mathutils 


class NbLatticeBoneWaveOperator(bpy.types.Operator):
    """选择晶格添加骨骼控制+挤压拉伸"""
    bl_idname = "object.add_lattice_bone_ctrl_wave_operator"
    bl_label = "NB Lattice Ctrl Wave"

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
        LATTICE_s=[]
        ARMATURE_s=[]
        if context.active_object != None:
            if context.mode == 'OBJECT':
                if len(context.selected_objects)>0:
                    for i in bpy.context.selected_objects:
                        if i.type == 'LATTICE':
                            LATTICE_s.append(i)
                        if i.type == 'ARMATURE':
                            ARMATURE_s.append(i)
                        if i.type == 'MESH':
                            MESH_s.append(i)
                            
        C = bpy.context
#        oldactive_bone=C.active_bone
        
        SelLattice =LATTICE_s[0]
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
        
        mesh = bpy.data.meshes.new('CBS_Sphere')
        CBS_sphere = bpy.data.objects.new("Basic_Sphere", mesh)
        #bpy.context.collection.objects.link(basic_sphere)
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm,subdivisions=1, radius=1.0)
        bm.to_mesh(mesh)
        bm.free()
        
        

        mesh = bpy.data.meshes.new('CBS_Cube')
        CBS_cube = bpy.data.objects.new("Basic_Cube", mesh)
        #bpy.context.collection.objects.link(basic_sphere)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm,size=1.0)
        bm.to_mesh(mesh)
        bm.free()
        
        
        
        arm.display_type = 'BBONE'
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
        
        bone1tName = adv_rename(bone1.name,"_t_ctrl")
        bone1t =arm.edit_bones.new(bone1tName)#尾部新建个骨骼
        if bpy.app.version[0]==3:
            bone1t.layers[8] = True
            bone1t.layers[1] = True

        bone1t.head =bone1.tail
        bone1t.tail =bone1.tail-bon_dir*bon_len*0.1
        bone1t.use_deform = False
        bone1t.parent = boneP
        
        bone1hName = adv_rename(bone1.name,"_h_ctrl")
        bone1h =arm.edit_bones.new(bone1hName)#头部新建个骨骼
        if bpy.app.version[0]==3:
            bone1h.layers[8] = True
            bone1h.layers[1] = True

        bone1h.head =bone1.head
        bone1h.tail =bone1.head-bon_dir*bon_len*0.1
        bone1h.use_deform = False
        bone1h.parent = boneP
        
        bone_Wave_C_Name = adv_rename(bone1.name,"_Wave_C")
        bone_Wave_C =arm.edit_bones.new(bone_Wave_C_Name)
        bone_Wave_C.head =bone1.head-bon_dir*bon_len*0.5
        bone_Wave_C.tail =bone_Wave_C.head-bon_dir*bon_len
        bone_Wave_C.length*=0.15
        bone_Wave_C.parent=boneP 

        bone_Wave_Range_Name =adv_rename(bone1.name,"_Wave_Range")
        bone_Wave_Range =arm.edit_bones.new(bone_Wave_Range_Name)
        bone_Wave_Range.head =bone1.tail
        bone_Wave_Range.tail =bone1.tail-bon_dir*bon_len
        bone_Wave_Range.length*=0.5
        bone_Wave_Range.parent=boneP
      


        bone1.bbone_custom_handle_start = bone1h
        bone1.bbone_handle_type_start ='TANGENT'
        bone1.bbone_custom_handle_end = bone1t
        bone1.bbone_handle_type_end = 'TANGENT'
        bone1.parent = bone1h
        bone1.inherit_scale = 'NONE'
        bone1.bbone_segments = 16
        bone1.bbone_z =bone1.bbone_x=bon_len*0.01
        bone1t.bbone_z =bone1t.bbone_x=bon_len*0.02
        bone1h.bbone_z =bone1h.bbone_x=bon_len*0.02
        bone1.bbone_z*=2
        
        bone1name=bone1.name
        bone_t_name=bone1t.name
        bone_h_name=bone1h.name
        
        bone1.bbone_handle_use_scale_start[0] = True
        bone1.bbone_handle_use_scale_start[1] = True
        bone1.bbone_handle_use_scale_start[2] = True
        bone1.bbone_handle_use_scale_end[0] = True
        bone1.bbone_handle_use_scale_end[1] = True
        bone1.bbone_handle_use_scale_end[2] = True
        
        
        
        pointNames=[]
        pointCo0 =[]
        pointCo1 =[]
        pointCo2 =[]
        pointCo3 =[]
        pointCo =[]
        

        for i,j in enumerate(SelLattice.data.points):
            if i%4==0:
                pointCo0.append(j.co)
            if i%4==1:
                pointCo1.append(j.co)
            if i%4==2:
                pointCo2.append(j.co)
            if i%4==3:
                pointCo3.append(j.co)
                
                
        for i,j in enumerate(pointCo0): 
            pointNames.append(SelLattice.name+str(i))
            pointCo.append((pointCo0[i]+pointCo1[i]+pointCo2[i]+pointCo3[i])/4)
            
        pointCo.reverse()
        pointNames.reverse()
        for i,j in enumerate(pointCo): 
            newBoneA_vertex_group = SelLattice.vertex_groups.new(name=pointNames[i])
            newBoneA_vertex_group.add([(i)*4-4,(i)*4-3,(i)*4-2,(i)*4-1,(i)*4,(i)*4+1,(i)*4+2,(i)*4+3], 1, 'REPLACE')
            

        modifier = SelLattice.modifiers.new(name=SelLattice.name+"ARMATURE", type='ARMATURE')
        modifier.object = o  
        modifier.use_deform_preserve_volume = True


        pointNames.reverse()

        bpy.ops.object.mode_set(mode='EDIT')
        
        
        
        if bpy.app.version[0]==4:
            NB_hide=arm.collections.get("NB_hide")
            if NB_hide is None:
                NB_hide=arm.collections.new("NB_hide")
                NB_hide.is_visible = False

            
        for i,j in enumerate(pointNames):
            if i<len(pointNames)-1:
                bone1 =arm.edit_bones.new(j)
                bone1.head =pointCo[i+1]
                bone1.tail =pointCo[i]
#                bone1.roll =math.pi
#                bone1.inherit_scale = 'NONE'
                
                bone2 =arm.edit_bones.new(j+"_off")
                bone2.head =pointCo[i+1]
                bone2.tail =pointCo[i]
#                bone2.roll =math.pi
                bone1.parent =bone2
                
                if bpy.app.version[0]==3:
                    bone1.layers[7] = True
                    bone1.layers[0] = False
                    bone2.layers[7] = True
                    bone2.layers[0] = False
                if bpy.app.version[0]==4:
                    NB_hide.assign(bone1)
                    NB_hide.assign(bone2)
        
        
        bpy.ops.object.mode_set(mode='POSE')

        
        
        for i,j in enumerate(pointNames):
            if i<len(pointNames)-1:
                ctCons =o.pose.bones[j+"_off"].constraints.new('COPY_TRANSFORMS')
                ctCons.target = o
                ctCons.subtarget = bone1Name
                ctCons.use_bbone_shape = True
                ctCons.head_tail = (14-i)/15




        
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_pattern(pattern=o.name,extend=False)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        
        bpy.ops.object.mode_set(mode='POSE')
        
        stCons =o.pose.bones.get(bone1Name).constraints.new('COPY_SCALE')
        stCons.target = o
        stCons.subtarget = bone_P_name
        
        stCons =o.pose.bones[bone1name].constraints.new('STRETCH_TO')
        stCons.target = o
        stCons.subtarget = bone1tName
#        stCons.volume = 'NO_VOLUME'


        o.pose.bones[bone_Wave_C_Name]["frequency"]=1.0
        o.pose.bones[bone_Wave_C_Name].id_properties_ui("frequency").update(min=0.0,max=20)

        o.pose.bones[bone_Wave_C_Name]["offset"]=0.0
        data_path = f'["{"offset"}"]'
        driver = o.pose.bones[bone_Wave_C_Name].driver_add(data_path)
        driver.driver.expression = '-frame/10'

        o.pose.bones[bone_Wave_Range_Name]["power"]=1.0
        o.pose.bones[bone_Wave_Range_Name].id_properties_ui("power").update(min=0.01,max=10)
        
        for i,j in enumerate(pointNames):
            if i<len(pointNames)-1:
                ###
                fc =o.pose.bones[j].driver_add("location",0)
                var1 = fc.driver.variables.new()
                var1.name = "x"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"].location[0]'   
                
                var1 = fc.driver.variables.new()
                var1.name = "o"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"]["offset"]' 
                
                var1 = fc.driver.variables.new()
                var1.name = "f"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"]["frequency"]' 
                
                var1 = fc.driver.variables.new()
                var1.name = "r"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_Range_Name+'"].scale[0]' 
                
                var1 = fc.driver.variables.new()
                var1.name = "d"
                var1.type = 'LOC_DIFF'
                var1.targets[0].id=o
                var1.targets[0].bone_target=bone_Wave_Range_Name
                var1.targets[1].id=o
                var1.targets[1].bone_target=j+"_off"
                
                var1 = fc.driver.variables.new()
                var1.name = "p"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_Range_Name+'"]["power"]'  
                
                
                fc.driver.expression ="sin("+str(i/16)+"*pi*f+o*pi)*x*pow(max((d-r)/(0-r),0),p)"

            ###
                fc =o.pose.bones[j].driver_add("location",2)
                var1 = fc.driver.variables.new()
                var1.name = "x"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"].location[2]'   
                
                var1 = fc.driver.variables.new()
                var1.name = "o"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"]["offset"]' 
                
                var1 = fc.driver.variables.new()
                var1.name = "f"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"]["frequency"]' 
                
                var1 = fc.driver.variables.new()
                var1.name = "r"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_Range_Name+'"].scale[0]' 
                
                var1 = fc.driver.variables.new()
                var1.name = "d"
                var1.type = 'LOC_DIFF'
                var1.targets[0].id=o
                var1.targets[0].bone_target=bone_Wave_Range_Name
                var1.targets[1].id=o
                var1.targets[1].bone_target=j+"_off"
                
                var1 = fc.driver.variables.new()
                var1.name = "p"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_Range_Name+'"]["power"]'  
                
                fc.driver.expression ="cos("+str(i/16)+"*pi*f+o*pi)*x*pow(max((d-r)/(0-r),0),p)"


            ###
            ###
                fc =o.pose.bones[j].driver_add("location",1)
                var1 = fc.driver.variables.new()
                var1.name = "x"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"].location[1]'   
                
                var1 = fc.driver.variables.new()
                var1.name = "o"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"]["offset"]' 
                
                var1 = fc.driver.variables.new()
                var1.name = "f"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"]["frequency"]' 
                
                var1 = fc.driver.variables.new()
                var1.name = "r"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_Range_Name+'"].scale[0]' 
                
                var1 = fc.driver.variables.new()
                var1.name = "d"
                var1.type = 'LOC_DIFF'
                var1.targets[0].id=o
                var1.targets[0].bone_target=bone_Wave_Range_Name
                var1.targets[1].id=o
                var1.targets[1].bone_target=j+"_off"
                
                var1 = fc.driver.variables.new()
                var1.name = "p"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_Range_Name+'"]["power"]'  
                
                
                fc.driver.expression ="sin("+str(i/16)+"*pi*f/2+pi/4+o*pi*2)*x*pow(max((d-r)/(0-r),0),p)"

            ###
#            ###
#                fc =o.pose.bones[j].driver_add("scale",1)
#                var1 = fc.driver.variables.new()
#                var1.name = "x"
#                var1.targets[0].id=o
#                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"].scale[1]'
#                   
#                var1 = fc.driver.variables.new()
#                var1.name = "o"
#                var1.targets[0].id=o
#                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"]["offset"]' 
#                
#                var1 = fc.driver.variables.new()
#                var1.name = "f"
#                var1.targets[0].id=o
#                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"]["frequency"]' 
#               
#                var1 = fc.driver.variables.new()
#                var1.name = "r"
#                var1.targets[0].id=o
#                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_Range_Name+'"].scale[0]' 
#                
#                var1 = fc.driver.variables.new()
#                var1.name = "d"
#                var1.type = 'LOC_DIFF'
#                var1.targets[0].id=o
#                var1.targets[0].bone_target=bone_Wave_Range_Name
#                var1.targets[1].id=o
#                var1.targets[1].bone_target=j+"_off"
#                
#                var1 = fc.driver.variables.new()
#                var1.name = "p"
#                var1.targets[0].id=o
#                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_Range_Name+'"]["power"]'  
#                
#                fc.driver.expression ="1+sin("+str(i/16)+"*pi*f+o*2+pi/6)*(x-1)*pow(max((d-r)/(0-r),0),p)"
            
              ###
                fc =o.pose.bones[j].driver_add("scale",0)
                var1 = fc.driver.variables.new()
                var1.name = "x"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"].scale[0]'
                   
                var1 = fc.driver.variables.new()
                var1.name = "o"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"]["offset"]' 
                
                var1 = fc.driver.variables.new()
                var1.name = "f"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"]["frequency"]' 
               
                var1 = fc.driver.variables.new()
                var1.name = "r"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_Range_Name+'"].scale[0]' 
                
                var1 = fc.driver.variables.new()
                var1.name = "d"
                var1.type = 'LOC_DIFF'
                var1.targets[0].id=o
                var1.targets[0].bone_target=bone_Wave_Range_Name
                var1.targets[1].id=o
                var1.targets[1].bone_target=j+"_off"
                
                var1 = fc.driver.variables.new()
                var1.name = "p"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_Range_Name+'"]["power"]'  
                
                fc.driver.expression ="1+sin("+str(i/16)+"*pi*f+o*pi*2+pi/4)*(x-1)*pow(max((d-r)/(0-r),0),p)"
                
                ###
                fc =o.pose.bones[j].driver_add("scale",2)
                var1 = fc.driver.variables.new()
                var1.name = "x"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"].scale[2]'
                   
                var1 = fc.driver.variables.new()
                var1.name = "o"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"]["offset"]' 
                
                var1 = fc.driver.variables.new()
                var1.name = "f"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"]["frequency"]' 
               
                var1 = fc.driver.variables.new()
                var1.name = "r"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_Range_Name+'"].scale[0]' 
                
                var1 = fc.driver.variables.new()
                var1.name = "d"
                var1.type = 'LOC_DIFF'
                var1.targets[0].id=o
                var1.targets[0].bone_target=bone_Wave_Range_Name
                var1.targets[1].id=o
                var1.targets[1].bone_target=j+"_off"
                
                var1 = fc.driver.variables.new()
                var1.name = "p"
                var1.targets[0].id=o
                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_Range_Name+'"]["power"]'  
                
                fc.driver.expression ="1+cos("+str(i/16)+"*pi*f+o*pi*2+pi/4)*(x-1)*pow(max((d-r)/(0-r),0),p)"
        
        o.pose.bones[bone_t_name].custom_shape = cbs
        o.pose.bones[bone1hName].custom_shape = cbs
        o.pose.bones.get(bone_P_name).custom_shape = cbs
        o.pose.bones[bone_Wave_C_Name].custom_shape = CBS_cube
        o.pose.bones[bone_Wave_Range_Name].custom_shape = cbs
        
       
        
       

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

















    
        if len(ARMATURE_s)==1 and ARMATURE_s[0].data.bones.active:
            oldactive_bone =ARMATURE_s[0].data.bones.active
            oldactive_boneName =oldactive_bone.name
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.armature.select_all(action='DESELECT')
            bone2tName = adv_rename(SelLattice.name, "_tt_ctrl")
            bone2t =arm.edit_bones.new(bone2tName)

            bone2t.head =arm.edit_bones[bone1tName].head
            bone2t.tail =arm.edit_bones[bone1tName].tail
            
            bone2t.use_deform = False
            
            bone2hName = adv_rename(SelLattice.name,"_hh_ctrl")
            bone2h =arm.edit_bones.new(bone2hName)#头部新建个骨骼
    
            bone2h.head =arm.edit_bones[bone1hName].head
            bone2h.tail =arm.edit_bones[bone1hName].tail
#            bone2t.roll =0
#            bone2h.roll =0
            bone2h.use_deform = False
                        
#            bone2PName = adv_rename(SelLattice.name,"_P_ctrl")
#            bone2P =arm.edit_bones.new(bone2PName)
#    
#            bone2P.head =arm.edit_bones[bone_P_name].head
#            bone2P.tail =arm.edit_bones[bone_P_name].tail
#            bone2P.use_deform = False
        
            bone2_Wave_C_Name = adv_rename(SelLattice.name,"_Wave_C_ctrl")
            bone2_Wave_C =arm.edit_bones.new(bone2_Wave_C_Name)
            bone2_Wave_C.head =arm.edit_bones[bone_Wave_C_Name].head
            bone2_Wave_C.tail =arm.edit_bones[bone_Wave_C_Name].tail
            bone2_Wave_C.use_deform = False
#            bone2_Wave_C.parent =bone2P


            bone2_Wave_Range_Name =adv_rename(SelLattice.name,"_Wave_Range_ctrl")
            bone2_Wave_Range =arm.edit_bones.new(bone2_Wave_Range_Name)
            bone2_Wave_Range.head =arm.edit_bones[bone_Wave_Range_Name].head
            bone2_Wave_Range.tail =arm.edit_bones[bone_Wave_Range_Name].tail
            bone2_Wave_Range.use_deform = False
#            bone2_Wave_Range.parent =bone2P


            
            arm.edit_bones[bone2tName].select=1
            arm.edit_bones[bone2hName].select=1
#            arm.edit_bones[bone2PName].select=1
            arm.edit_bones[bone2_Wave_C_Name].select=1
            arm.edit_bones[bone2_Wave_Range_Name].select=1
  
            
            bpy.ops.armature.separate()

            bpy.ops.object.mode_set(mode='OBJECT')  
        
        
        
        
            separateArm =bpy.context.selected_objects[1]
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_pattern(pattern=separateArm.name,extend=True)

            bpy.ops.object.select_pattern(pattern=ARMATURE_s[0].name,extend=True)
            bpy.context.view_layer.objects.active=ARMATURE_s[0]
            bpy.ops.object.join()

            bpy.ops.object.mode_set(mode='EDIT')
#            ARMATURE_s[0].data.edit_bones[bone2PName].parent=ARMATURE_s[0].data.edit_bones[oldactive_boneName]
            ARMATURE_s[0].data.edit_bones[bone2tName].parent=ARMATURE_s[0].data.edit_bones[oldactive_boneName]
            ARMATURE_s[0].data.edit_bones[bone2hName].parent=ARMATURE_s[0].data.edit_bones[oldactive_boneName]
            ARMATURE_s[0].data.edit_bones[bone2_Wave_C_Name].parent=ARMATURE_s[0].data.edit_bones[oldactive_boneName]
            ARMATURE_s[0].data.edit_bones[bone2_Wave_Range_Name].parent=ARMATURE_s[0].data.edit_bones[oldactive_boneName]
   
            
            
            bpy.ops.object.mode_set(mode='POSE')
            ARMATURE_s[0].pose.bones[bone2tName].custom_shape = cbs
            ARMATURE_s[0].pose.bones[bone2hName].custom_shape = cbs
#            ARMATURE_s[0].pose.bones[bone2PName].custom_shape = cbs 
            ARMATURE_s[0].pose.bones[bone2_Wave_C_Name].custom_shape = CBS_cube
            ARMATURE_s[0].pose.bones[bone2_Wave_Range_Name].custom_shape = cbs 
            ARMATURE_s[0].pose.bones[bone2tName].custom_shape_scale_xyz[0] = 1.2
            ARMATURE_s[0].pose.bones[bone2tName].custom_shape_scale_xyz[1] = 1.2
            ARMATURE_s[0].pose.bones[bone2tName].custom_shape_scale_xyz[2] = 1.2
            ARMATURE_s[0].pose.bones[bone2hName].custom_shape_scale_xyz[0] = 1.2
            ARMATURE_s[0].pose.bones[bone2hName].custom_shape_scale_xyz[1] = 1.2
            ARMATURE_s[0].pose.bones[bone2hName].custom_shape_scale_xyz[2] = 1.2
            
#            ARMATURE_s[0].pose.bones[bone2PName].custom_shape_scale_xyz[0] = 1.3
#            ARMATURE_s[0].pose.bones[bone2PName].custom_shape_scale_xyz[1] = 1.3
#            ARMATURE_s[0].pose.bones[bone2PName].custom_shape_scale_xyz[2] = 1.3
            

            ARMATURE_s[0].pose.bones[bone2_Wave_C_Name]["frequency"]=1.0
            ARMATURE_s[0].pose.bones[bone2_Wave_C_Name].id_properties_ui("frequency").update(min=0.0,max=20)

            ARMATURE_s[0].pose.bones[bone2_Wave_C_Name]["offset"]=0.0
            data_path = f'["{"offset"}"]'
            driver = ARMATURE_s[0].pose.bones[bone2_Wave_C_Name].driver_add(data_path)
            driver.driver.expression = '-frame/10'

            ARMATURE_s[0].pose.bones[bone2_Wave_Range_Name]["power"]=1.0
            ARMATURE_s[0].pose.bones[bone2_Wave_Range_Name].id_properties_ui("power").update(min=0.01,max=10)
            
            
            
            
            ctCons =o.pose.bones[bone1tName].constraints.new('COPY_TRANSFORMS')
            ctCons.target = ARMATURE_s[0]
            ctCons.subtarget = bone2tName  
            o.pose.bones[bone1tName].constraints.move(o.pose.bones[bone1tName].constraints.find(ctCons.name),0)

            ctCons =o.pose.bones[bone1tName].constraints.new('COPY_ROTATION')
            ctCons.target = ARMATURE_s[0]
            ctCons.subtarget = bone2tName  
            ctCons.mix_mode = 'ADD'
            ctCons.target_space = 'LOCAL'
            ctCons.owner_space = 'LOCAL'


            ctCons =o.pose.bones[bone1hName].constraints.new('COPY_TRANSFORMS')
            ctCons.target = ARMATURE_s[0]
            ctCons.subtarget = bone2hName
            o.pose.bones[bone1hName].constraints.move(o.pose.bones[bone1hName].constraints.find(ctCons.name),0)
            
            ctCons =o.pose.bones[bone1hName].constraints.new('COPY_ROTATION')
            ctCons.target = ARMATURE_s[0]
            ctCons.subtarget = bone2hName  
            ctCons.mix_mode = 'ADD'
            ctCons.target_space = 'LOCAL'
            ctCons.owner_space = 'LOCAL'
            
        


            for i,j in enumerate(pointNames):
                if i<len(pointNames)-1:
                    
                    o.pose.bones[j].driver_remove("location",0)
                    ###
                    
                    fc =o.pose.bones[j].driver_add("location",0)
                    var1 = fc.driver.variables.new()
                    var1.name = "x"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_C_Name+'"].location[0]'   
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "o"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_C_Name+'"]["offset"]' 
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "f"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_C_Name+'"]["frequency"]' 
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "r"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_Range_Name+'"].scale[0]' 
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "d"
                    var1.type = 'LOC_DIFF'
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].bone_target=bone2_Wave_Range_Name
                    var1.targets[1].id=o
                    var1.targets[1].bone_target=j+"_off"
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "p"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_Range_Name+'"]["power"]'  
                    
                    
                    fc.driver.expression ="sin("+str(i/16)+"*pi*f+o*pi)*x*pow(max((d-r)/(0-r),0),p)"

                ###
                    o.pose.bones[j].driver_remove("location",2)
                    fc =o.pose.bones[j].driver_add("location",2)
                    var1 = fc.driver.variables.new()
                    var1.name = "x"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_C_Name+'"].location[2]'   
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "o"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_C_Name+'"]["offset"]' 
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "f"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_C_Name+'"]["frequency"]' 
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "r"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_Range_Name+'"].scale[0]' 
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "d"
                    var1.type = 'LOC_DIFF'
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].bone_target=bone2_Wave_Range_Name
                    var1.targets[1].id=o
                    var1.targets[1].bone_target=j+"_off"
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "p"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_Range_Name+'"]["power"]'  
                    
                    fc.driver.expression ="cos("+str(i/16)+"*pi*f+o*pi)*x*pow(max((d-r)/(0-r),0),p)"


                ###
                ###
                    o.pose.bones[j].driver_remove("location",1)
                    fc =o.pose.bones[j].driver_add("location",1)
                    var1 = fc.driver.variables.new()
                    var1.name = "x"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_C_Name+'"].location[1]'   
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "o"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_C_Name+'"]["offset"]' 
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "f"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_C_Name+'"]["frequency"]' 
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "r"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_Range_Name+'"].scale[0]' 
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "d"
                    var1.type = 'LOC_DIFF'
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].bone_target=bone2_Wave_Range_Name
                    var1.targets[1].id=o
                    var1.targets[1].bone_target=j+"_off"
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "p"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_Range_Name+'"]["power"]'  
                    
                    
                    fc.driver.expression ="sin("+str(i/16)+"*pi*f/2+pi/4+o*pi*2)*x*pow(max((d-r)/(0-r),0),p)"

                ###
    #            ###
    #                fc =o.pose.bones[j].driver_add("scale",1)
    #                var1 = fc.driver.variables.new()
    #                var1.name = "x"
    #                var1.targets[0].id=o
    #                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"].scale[1]'
    #                   
    #                var1 = fc.driver.variables.new()
    #                var1.name = "o"
    #                var1.targets[0].id=o
    #                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"]["offset"]' 
    #                
    #                var1 = fc.driver.variables.new()
    #                var1.name = "f"
    #                var1.targets[0].id=o
    #                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_C_Name+'"]["frequency"]' 
    #               
    #                var1 = fc.driver.variables.new()
    #                var1.name = "r"
    #                var1.targets[0].id=o
    #                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_Range_Name+'"].scale[0]' 
    #                
    #                var1 = fc.driver.variables.new()
    #                var1.name = "d"
    #                var1.type = 'LOC_DIFF'
    #                var1.targets[0].id=o
    #                var1.targets[0].bone_target=bone_Wave_Range_Name
    #                var1.targets[1].id=o
    #                var1.targets[1].bone_target=j+"_off"
    #                
    #                var1 = fc.driver.variables.new()
    #                var1.name = "p"
    #                var1.targets[0].id=o
    #                var1.targets[0].data_path = 'pose.bones["'+bone_Wave_Range_Name+'"]["power"]'  
    #                
    #                fc.driver.expression ="1+sin("+str(i/16)+"*pi*f+o*2+pi/6)*(x-1)*pow(max((d-r)/(0-r),0),p)"
                
                  ###
                    o.pose.bones[j].driver_remove("scale",0)
                    fc =o.pose.bones[j].driver_add("scale",0)
                    var1 = fc.driver.variables.new()
                    var1.name = "x"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_C_Name+'"].scale[0]'
                       
                    var1 = fc.driver.variables.new()
                    var1.name = "o"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_C_Name+'"]["offset"]' 
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "f"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_C_Name+'"]["frequency"]' 
                   
                    var1 = fc.driver.variables.new()
                    var1.name = "r"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_Range_Name+'"].scale[0]' 
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "d"
                    var1.type = 'LOC_DIFF'
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].bone_target=bone2_Wave_Range_Name
                    var1.targets[1].id=o
                    var1.targets[1].bone_target=j+"_off"
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "p"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_Range_Name+'"]["power"]'  
                    
                    fc.driver.expression ="1+sin("+str(i/16)+"*pi*f+o*pi*2+pi/4)*(x-1)*pow(max((d-r)/(0-r),0),p)"
                    
                    ###
                    o.pose.bones[j].driver_remove("scale",2)
                    fc =o.pose.bones[j].driver_add("scale",2)
                    var1 = fc.driver.variables.new()
                    var1.name = "x"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_C_Name+'"].scale[2]'
                       
                    var1 = fc.driver.variables.new()
                    var1.name = "o"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_C_Name+'"]["offset"]' 
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "f"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_C_Name+'"]["frequency"]' 
                   
                    var1 = fc.driver.variables.new()
                    var1.name = "r"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_Range_Name+'"].scale[0]' 
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "d"
                    var1.type = 'LOC_DIFF'
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].bone_target=bone2_Wave_Range_Name
                    var1.targets[1].id=o
                    var1.targets[1].bone_target=j+"_off"
                    
                    var1 = fc.driver.variables.new()
                    var1.name = "p"
                    var1.targets[0].id=ARMATURE_s[0]
                    var1.targets[0].data_path = 'pose.bones["'+bone2_Wave_Range_Name+'"]["power"]'  
                    
                    fc.driver.expression ="1+cos("+str(i/16)+"*pi*f+o*pi*2+pi/4)*(x-1)*pow(max((d-r)/(0-r),0),p)"
            



                

            bpy.ops.object.mode_set(mode='OBJECT') 
            bpy.ops.object.select_pattern(pattern=o.name,extend=True)
            bpy.ops.object.select_pattern(pattern=SelLattice.name,extend=True)
            bpy.ops.object.parent_set(type='BONE')
            o.users_collection[0].objects.unlink(o)
            ARMATURE_s[0].users_collection[0].objects.link(o)
            o.hide_viewport = True
            o.hide_render = True

            bpy.ops.object.mode_set(mode='POSE')


        bpy.ops.ed.undo_push(message="NB")
        return {'FINISHED'}



















classes=(
NbLatticeBoneWaveOperator,
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






