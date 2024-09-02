import bpy
import math 
import bmesh
import mathutils 


class NbCurveLatticeOperator(bpy.types.Operator):
    """晶格加曲线加骨骼"""
    bl_idname = "object.add_nbcurvelatticeoperator"
    bl_label = "NB Lattice Curve"

    number: bpy.props.IntProperty(name='Number', default=20, min=3, max=64)
   

    def invoke(self, context,event):
        wm =context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="w")
        column = layout.column()

        row = column.row(align=True)
        row.prop(self, "number")

    
    @classmethod
    def poll(cls, context):
        a=0
        MESH_s=[]
        LATTICE_s=[]
        ARMATURE_s=[]
        CURVE_s=[]
        if context.mode == 'OBJECT':
            if len(context.selected_objects)>0:
                for i in bpy.context.selected_objects:
                    if i.type == 'LATTICE':
                        LATTICE_s.append(i)
                    if i.type == 'ARMATURE':
                        ARMATURE_s.append(i)  
                    if i.type == 'CURVE':
                        CURVE_s.append(i)
        if len(LATTICE_s)==1 and len(ARMATURE_s)==1 and len(CURVE_s)==1:
            a=1
                
                    
        return a
    
    
    def execute(self, context):
        MESH_s=[]
        for i in bpy.context.selected_objects:
            if i.type == 'LATTICE':
                Lattice = i
            if i.type == 'ARMATURE':
                ARMATURE= i
            if i.type == 'CURVE':
                CURVE= i
            if i.type == 'MESH':
                MESH_s.append(i)
                
        rootArm =ARMATURE
        rootBone =ARMATURE.data.bones.active
        rootBoneName=rootBone.name

        armName =Lattice.name+"_Arm"
        arm = bpy.data.armatures.new(armName)
        o=bpy.data.objects.new(armName,arm)

        rootArm.users_collection[0].objects.link(o)

          
        o.show_in_front = True
        bpy.context.view_layer.objects.active=o
        o.matrix_world=Lattice.matrix_world

        cbsK=bpy.data.objects.new("NB",None)
        cbsK.empty_display_type = 'CUBE'

        cbsA=bpy.data.objects.new("CBS_Arrow",None)
        cbsA.empty_display_type = 'SINGLE_ARROW'

        cbsS=bpy.data.objects.new("CBS_SPHERE",None)
        cbsS.empty_display_type = 'SPHERE'

        mesh = bpy.data.meshes.new('CBS_Sphere')
        CBS_sphere = bpy.data.objects.new("Basic_Sphere", mesh)
        #bpy.context.collection.objects.link(basic_sphere)
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm,subdivisions=2, radius=0.2)
        bm.to_mesh(mesh)
        bm.free()

        mesh = bpy.data.meshes.new('CBS_Cube')
        CBS_cube = bpy.data.objects.new("Basic_Cube", mesh)
        #bpy.context.collection.objects.link(basic_sphere)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm,size=1.0)
        bm.to_mesh(mesh)
        bm.free()



        num =self.number
        Lattice.data.points_w = num
        
        Lattice.animation_data_clear()
        Lattice.data.interpolation_type_u = 'KEY_LINEAR'
        Lattice.data.interpolation_type_v = 'KEY_LINEAR'
        Lattice.data.interpolation_type_w = 'KEY_LINEAR'




        pointNames=[]
        pointCo0 =[]
        pointCo1 =[]
        pointCo2 =[]
        pointCo3 =[]
        pointCo =[]

        for i,j in enumerate(Lattice.data.points):
            if i%4==0:
                pointCo0.append(j.co)
            if i%4==1:
                pointCo1.append(j.co)
            if i%4==2:
                pointCo2.append(j.co)
            if i%4==3:
                pointCo3.append(j.co)
                
                
        for i,j in enumerate(pointCo0): 
            pointNames.append(Lattice.name+str(i))
            pointCo.append((pointCo0[i]+pointCo1[i]+pointCo2[i]+pointCo3[i])/4)
            
        pointCo.reverse()
        pointNames.reverse()
        for i,j in enumerate(pointCo): 
            newBoneA_vertex_group = Lattice.vertex_groups.new(name=pointNames[i])
            newBoneA_vertex_group.add([(i)*4-4,(i)*4-3,(i)*4-2,(i)*4-1,(i)*4,(i)*4+1,(i)*4+2,(i)*4+3], 1, 'REPLACE')
            

        modifier = Lattice.modifiers.new(name=Lattice.name+"ARMATURE", type='ARMATURE')
        modifier.object = o  
        modifier.use_deform_preserve_volume = True


        pointNames.reverse()

        bpy.ops.object.mode_set(mode='EDIT')

        editbones=[]
        for i,j in enumerate(pointNames):
            if i<len(pointNames)-1:
                bone1 =arm.edit_bones.new(j)
                bone1.head =pointCo[i]
                bone1.tail =pointCo[i+1]
                bone1.roll =math.pi
                editbones.append(bone1)
                bone1.inherit_scale = 'NONE'

                
        for i,bone in enumerate(editbones):
            if i >0:
                bone.parent =editbones[i-1]

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_pattern(pattern=o.name,extend=False)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


            
        P_head =Lattice.matrix_world @ mathutils.Vector((0.0,0.0,0.0))
        P_tail =Lattice.matrix_world @ mathutils.Vector((0.0,0.0,-1.0))

        Lattice.rotation_euler[0] = 0
        Lattice.rotation_euler[1] = 0
        Lattice.rotation_euler[2] = 0
        Lattice.rotation_quaternion[0]=1
        Lattice.rotation_quaternion[1]=0
        Lattice.rotation_quaternion[2]=0
        Lattice.rotation_quaternion[3]=0
        Lattice.location[0] = 0
        Lattice.location[1] = 0
        Lattice.location[2] = 0

        o.rotation_euler[0] = 0
        o.rotation_euler[1] = 0
        o.rotation_euler[2] = 0
        o.rotation_quaternion[0]=1
        o.rotation_quaternion[1]=0
        o.rotation_quaternion[2]=0
        o.rotation_quaternion[3]=0
        o.location[0] = 0
        o.location[1] = 0
        o.location[2] = 0

        Lattice.parent = o
        #o.location[2] = -Lattice.scale[2]/2
        #bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)







        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active=rootArm
        bpy.ops.object.select_pattern(pattern=rootArm.name,extend=True)
        bpy.ops.object.mode_set(mode='EDIT')

        lll=Lattice.scale[2]/(num-1)

        bone_P =rootArm.data.edit_bones.new(Lattice.name+"_P")
        bone_P.head =P_head
        bone_P.tail =P_tail
        bone_P.length*=0.5

        bone_FP =rootArm.data.edit_bones.new(Lattice.name+"_FP")
        bone_FP.head =mathutils.Vector((0.0,0.0,0.0))
        bone_FP.tail =mathutils.Vector((0.0,0.0,1.0))
        bone_FP.length*=lll

        bone_C =rootArm.data.edit_bones.new(Lattice.name+"_C")
        bone_C.head =mathutils.Vector((0.0,0.0,-Lattice.scale[2]/2))
        bone_C.tail =mathutils.Vector((0.0,0.0,-Lattice.scale[2]/2-1))
        bone_C.length*=2
        bone_C.parent=bone_FP


        bone_CT =rootArm.data.edit_bones.new(Lattice.name+"_CT")
        bone_CT.head =mathutils.Vector((0.0,0.0,Lattice.scale[2]/2))
        bone_CT.tail =mathutils.Vector((0.0,0.0,Lattice.scale[2]/2+1))
        bone_CT.length*=1.0
        bone_CT.parent=bone_FP


        bone_Wave_C =rootArm.data.edit_bones.new(Lattice.name+"_Wave_C")
        bone_Wave_C.head =mathutils.Vector((0.0,0.0,-Lattice.scale[2]/2))
        bone_Wave_C.tail =mathutils.Vector((0.0,0.0,-Lattice.scale[2]/2+1))
        bone_Wave_C.length*=0.3
        bone_Wave_C.parent=bone_FP


        bone_Wave_Range =rootArm.data.edit_bones.new(Lattice.name+"_Wave_Range")
        bone_Wave_Range.head =mathutils.Vector((0.0,0.0,Lattice.scale[2]/4))
        bone_Wave_Range.tail =mathutils.Vector((0.0,0.0,Lattice.scale[2]/2+1))
        bone_Wave_Range.length*=1


        if bpy.app.version[0]==4:
            NB_hide=rootArm.data.collections.get("NB_hide")
            if NB_hide is None:
                NB_hide=rootArm.data.collections.new("NB_hide")
                NB_hide.is_visible = False

        if bpy.app.version[0]==3:
            bone_P.layers[7] = True
            bone_P.layers[0] = False
            bone_FP.layers[7] = True
            bone_FP.layers[0] = False
        if bpy.app.version[0]==4:
            NB_hide.assign(bone_P)
            NB_hide.assign(bone_FP)


        for i,j in enumerate(pointNames):
            bone =rootArm.data.edit_bones.new(j)
            bone.head =mathutils.Vector((0.0,0.0,0.0))
            bone.tail =mathutils.Vector((0.0,0.0,1.0))
            bone.length*=lll
            
            bone2 =rootArm.data.edit_bones.new(j+"_c")
            bone2.head =mathutils.Vector((0.0,0.0,0.0))
            bone2.tail =mathutils.Vector((0.0,0.0,1.0))
            bone2.length*=lll
            
            if bpy.app.version[0]==3:
                bone.layers[7] = True
                bone.layers[0] = False
                bone2.layers[7] = True
                bone2.layers[0] = False
            if bpy.app.version[0]==4:
                NB_hide.assign(bone)
                NB_hide.assign(bone2)
              
            if i ==len(pointNames)-1:
                bone_Wave_Range.parent=bone2
            
        bpy.ops.object.mode_set(mode='POSE')

        ctCons =rootArm.pose.bones[rootBoneName].constraints.new('ARMATURE')
        ctCons.targets.new()
        ctCons.targets[0].target = rootArm
        ctCons.targets[0].subtarget = Lattice.name+"_P"


        ctCons =rootArm.pose.bones[Lattice.name+"_P"].constraints.new('COPY_TRANSFORMS')
        ctCons.target = rootArm
        ctCons.subtarget = Lattice.name+"_FP"

        ctCons =rootArm.pose.bones[Lattice.name+"_FP"].constraints.new('FOLLOW_PATH')
        ctCons.target = CURVE
        ctCons.forward_axis = 'TRACK_NEGATIVE_Z'
        ctCons.up_axis = 'UP_Y'
        ctCons.use_fixed_location = True
        ctCons.use_curve_follow = True

        ctCons.driver_remove("offset_factor")
        fc =ctCons.driver_add("offset_factor")

        var1 = fc.driver.variables.new()
        var1.name = "v"
        var1.targets[0].id=rootArm
        var1.type = 'SINGLE_PROP'
        var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_C"+'"].location[1]'   
        fc.driver.expression ="v"


        rootArm.pose.bones[Lattice.name+"_C"].lock_location[0] = True
        rootArm.pose.bones[Lattice.name+"_C"].lock_location[2] = True
        rootArm.pose.bones[Lattice.name+"_C"].lock_rotation_w = True
        rootArm.pose.bones[Lattice.name+"_C"].lock_rotation[0] = True
        rootArm.pose.bones[Lattice.name+"_C"].lock_rotation[1] = True
        rootArm.pose.bones[Lattice.name+"_C"].lock_rotation[2] = True
        rootArm.pose.bones[Lattice.name+"_C"].lock_scale[0] = True
        rootArm.pose.bones[Lattice.name+"_C"].lock_scale[1] = True
        rootArm.pose.bones[Lattice.name+"_C"].lock_scale[2] = True

        rootArm.pose.bones[Lattice.name+"_CT"].lock_location[0] = True
        rootArm.pose.bones[Lattice.name+"_CT"].lock_location[2] = True
        rootArm.pose.bones[Lattice.name+"_CT"].lock_rotation_w = True
        rootArm.pose.bones[Lattice.name+"_CT"].lock_rotation[0] = True
        rootArm.pose.bones[Lattice.name+"_CT"].lock_rotation[1] = True
        rootArm.pose.bones[Lattice.name+"_CT"].lock_rotation[2] = True
        rootArm.pose.bones[Lattice.name+"_CT"].lock_scale[0] = True
        rootArm.pose.bones[Lattice.name+"_CT"].lock_scale[1] = True
        rootArm.pose.bones[Lattice.name+"_CT"].lock_scale[2] = True

        rootArm.pose.bones[Lattice.name+"_Wave_C"].lock_location[1] = True
        rootArm.pose.bones[Lattice.name+"_Wave_C"].lock_rotation_w = True
        rootArm.pose.bones[Lattice.name+"_Wave_C"].lock_rotation[0] = True
        rootArm.pose.bones[Lattice.name+"_Wave_C"].lock_rotation[1] = True
        rootArm.pose.bones[Lattice.name+"_Wave_C"].lock_rotation[2] = True
#        rootArm.pose.bones[Lattice.name+"_Wave_C"].lock_scale[0] = True
#        rootArm.pose.bones[Lattice.name+"_Wave_C"].lock_scale[1] = True
#        rootArm.pose.bones[Lattice.name+"_Wave_C"].lock_scale[2] = True

        rootArm.pose.bones[Lattice.name+"_C"].custom_shape = cbsA
        rootArm.pose.bones[Lattice.name+"_C"].custom_shape_rotation_euler[0] = -1.5708

        rootArm.pose.bones[Lattice.name+"_CT"].custom_shape = CBS_sphere
        rootArm.pose.bones[Lattice.name+"_Wave_C"].custom_shape = CBS_cube
        rootArm.pose.bones[Lattice.name+"_Wave_Range"].custom_shape = cbsS



        ctCons =rootArm.pose.bones[Lattice.name+"_C"].constraints.new('LIMIT_LOCATION')
        ctCons.use_min_y = True
        ctCons.use_max_y = True
        ctCons.max_y = 1
        ctCons.use_transform_limit = True
        ctCons.owner_space = 'LOCAL'
        
########################################
        rootArm.pose.bones[Lattice.name+"_CT"]["power"]=1.0
        rootArm.pose.bones[Lattice.name+"_CT"].id_properties_ui("power").update(min=0.01,max=10)
        
        
        rootArm.pose.bones[Lattice.name+"_C"]["curveLength"]=1.0
        rootArm.pose.bones[Lattice.name+"_C"].id_properties_ui("curveLength").update(min=0,max=20000)
        rootArm.pose.bones[Lattice.name+"_C"]["Follow Curve"]=True
        rootArm.pose.bones[Lattice.name+"_C"]["Curve Raduis"]=True



        data_path = f'["{"curveLength"}"]'
        driver = rootArm.pose.bones[Lattice.name+"_C"].driver_add(data_path)
        driver.driver.expression = 'bpy.data.objects["'+CURVE.name+'"].data.splines[0].calc_length()'

        rootArm.pose.bones[Lattice.name+"_Wave_C"]["frequency"]=1.0
        rootArm.pose.bones[Lattice.name+"_Wave_C"].id_properties_ui("frequency").update(min=0.0,max=20)

        rootArm.pose.bones[Lattice.name+"_Wave_C"]["offset"]=0.0
        data_path = f'["{"offset"}"]'
        driver = rootArm.pose.bones[Lattice.name+"_Wave_C"].driver_add(data_path)
        driver.driver.expression = '-frame/2'

        rootArm.pose.bones[Lattice.name+"_Wave_Range"]["power"]=1.0
        rootArm.pose.bones[Lattice.name+"_Wave_Range"].id_properties_ui("power").update(min=0.01,max=10)



                
        for i,j in enumerate(pointNames):
            ctCons =rootArm.pose.bones[j].constraints.new('FOLLOW_PATH')
            ctCons.target = CURVE
            ctCons.forward_axis = 'TRACK_NEGATIVE_Z'
            ctCons.up_axis = 'UP_Y'
            ctCons.use_fixed_location = True
            ctCons.use_curve_follow = True
            
            ctCons.driver_remove("offset_factor")
            fc =ctCons.driver_add("offset_factor")

            var1 = fc.driver.variables.new()
            var1.name = "v"
            var1.targets[0].id=rootArm
        #    var1.type = 'SINGLE_PROP'
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_C"+'"].location[1]'   
        #    fc.driver.expression ="v"
            
            var1 = fc.driver.variables.new()
            var1.name = "o"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_CT"+'"].location[1]'   
        #    fc.driver.expression ="o"
            
            var1 = fc.driver.variables.new()
            var1.name = "c"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_C"+'"]["curveLength"]'   
        #    fc.driver.expression ="o"

            var1 = fc.driver.variables.new()
            var1.name = "p"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_CT"+'"]["power"]'   
        #    fc.driver.expression ="o"

            fc.driver.expression ="v-("+str(lll)+"*"+str(i)+"-"+str(Lattice.scale[2]/2)+"+o*pow("+str(i/num)+",p))/c"
            
            
            
            ctCons.driver_remove("use_curve_radius")
            fc =ctCons.driver_add("use_curve_radius")

            var1 = fc.driver.variables.new()
            var1.name = "v"
            var1.targets[0].id=rootArm
        #    var1.type = 'SINGLE_PROP'
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_C"+'"]["Curve Raduis"]'   
            fc.driver.expression ="v"
            
            
            
            ###
            ctCons =rootArm.pose.bones[j+"_c"].constraints.new('FOLLOW_PATH')
            ctCons.target = CURVE
            ctCons.forward_axis = 'TRACK_NEGATIVE_Z'
            ctCons.up_axis = 'UP_Y'
            ctCons.use_fixed_location = True
            ctCons.use_curve_follow = True
            
            ctCons.driver_remove("offset_factor")
            fc =ctCons.driver_add("offset_factor")

            var1 = fc.driver.variables.new()
            var1.name = "v"
            var1.targets[0].id=rootArm
        #    var1.type = 'SINGLE_PROP'
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_C"+'"].location[1]'   
        #    fc.driver.expression ="v"
            
            var1 = fc.driver.variables.new()
            var1.name = "o"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_CT"+'"].location[1]'   
        #    fc.driver.expression ="o"
            
            var1 = fc.driver.variables.new()
            var1.name = "c"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_C"+'"]["curveLength"]'   
        #    fc.driver.expression ="o"

            var1 = fc.driver.variables.new()
            var1.name = "p"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_CT"+'"]["power"]'   
        #    fc.driver.expression ="o"

            fc.driver.expression ="v-("+str(lll)+"*"+str(i)+"-"+str(Lattice.scale[2]/2)+"+o*pow("+str(i/num)+",p))/c"
            
            ###
            fc =rootArm.pose.bones[j].driver_add("location",0)
            var1 = fc.driver.variables.new()
            var1.name = "x"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_Wave_C"+'"].location[0]'   
            
            var1 = fc.driver.variables.new()
            var1.name = "o"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_Wave_C"+'"]["offset"]' 
            
            var1 = fc.driver.variables.new()
            var1.name = "f"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_Wave_C"+'"]["frequency"]' 
            
            var1 = fc.driver.variables.new()
            var1.name = "r"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_Wave_Range"+'"].scale[0]' 
            
            var1 = fc.driver.variables.new()
            var1.name = "d"
            var1.type = 'LOC_DIFF'
            var1.targets[0].id=rootArm
            var1.targets[0].bone_target=Lattice.name+"_Wave_Range"
            var1.targets[1].id=rootArm
            var1.targets[1].bone_target=j+"_c"
            
            var1 = fc.driver.variables.new()
            var1.name = "p"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_Wave_Range"+'"]["power"]'  
            
            
            fc.driver.expression ="sin("+str(i/num)+"*pi*f+o)*x*pow(max((d-r)/(0-r),0),p)"

        ###
            fc =rootArm.pose.bones[j].driver_add("location",2)
            var1 = fc.driver.variables.new()
            var1.name = "x"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_Wave_C"+'"].location[2]'   
            
            var1 = fc.driver.variables.new()
            var1.name = "o"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_Wave_C"+'"]["offset"]' 
            
            var1 = fc.driver.variables.new()
            var1.name = "f"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_Wave_C"+'"]["frequency"]' 
            
            var1 = fc.driver.variables.new()
            var1.name = "r"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_Wave_Range"+'"].scale[0]' 
            
            var1 = fc.driver.variables.new()
            var1.name = "d"
            var1.type = 'LOC_DIFF'
            var1.targets[0].id=rootArm
            var1.targets[0].bone_target=Lattice.name+"_Wave_Range"
            var1.targets[1].id=rootArm
            var1.targets[1].bone_target=j+"_c"
            
            var1 = fc.driver.variables.new()
            var1.name = "p"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_Wave_Range"+'"]["power"]'  
            
            fc.driver.expression ="cos("+str(i/num)+"*pi*f+o)*x*pow(max((d-r)/(0-r),0),p)"


        ###
            fc =rootArm.pose.bones[j].driver_add("scale",1)
            var1 = fc.driver.variables.new()
            var1.name = "x"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_Wave_C"+'"].scale[0]'
               
            var1 = fc.driver.variables.new()
            var1.name = "o"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_Wave_C"+'"]["offset"]' 
            
            var1 = fc.driver.variables.new()
            var1.name = "f"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_Wave_C"+'"]["frequency"]' 
           
            var1 = fc.driver.variables.new()
            var1.name = "r"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_Wave_Range"+'"].scale[0]' 
            
            var1 = fc.driver.variables.new()
            var1.name = "d"
            var1.type = 'LOC_DIFF'
            var1.targets[0].id=rootArm
            var1.targets[0].bone_target=Lattice.name+"_Wave_Range"
            var1.targets[1].id=rootArm
            var1.targets[1].bone_target=j+"_c"
            
            var1 = fc.driver.variables.new()
            var1.name = "p"
            var1.targets[0].id=rootArm
            var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_Wave_Range"+'"]["power"]'  
            
            fc.driver.expression ="1+sin("+str(i/num)+"*pi*f+o+pi/6)*(x-1)*pow(max((d-r)/(0-r),0),p)"





            
        ctCons =o.constraints.new('FOLLOW_PATH')
        ctCons.target = CURVE
        ctCons.forward_axis = 'FORWARD_Z'
        ctCons.up_axis = 'UP_Y'
        ctCons.use_fixed_location = True
        ctCons.use_curve_follow = True
        ctCons.driver_remove("offset_factor")
        fc =ctCons.driver_add("offset_factor")

        var1 = fc.driver.variables.new()
        var1.name = "v"
        var1.targets[0].id=rootArm
        var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_C"+'"].location[1]'   
        fc.driver.expression ="v"



        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active=o
        bpy.ops.object.select_pattern(pattern=o.name,extend=True)
        bpy.ops.object.mode_set(mode='POSE')


        for i,j in enumerate(pointNames):
            if i==0:
                ctCons =o.pose.bones[j].constraints.new('COPY_LOCATION')
                ctCons.target = rootArm
                ctCons.subtarget=j
            if i<len(pointNames)-1:    
                ctCons =o.pose.bones[j].constraints.new('COPY_ROTATION')
                ctCons.target = rootArm
                ctCons.subtarget=j
#                ctCons.use_x = False
#                ctCons.use_z = False
#                ctCons.target_space = 'LOCAL'
#                ctCons.owner_space = 'LOCAL'
#                ctCons.influence = 1
                fc =ctCons.driver_add("influence")
                var1 = fc.driver.variables.new()
                var1.name = "v"
                var1.targets[0].id=rootArm
                var1.targets[0].data_path = 'pose.bones["'+Lattice.name+"_C"+'"]["Follow Curve"]'   
                fc.driver.expression ="v"


                ctCons =o.pose.bones[j].constraints.new('COPY_SCALE')
                ctCons.target = rootArm
                ctCons.subtarget=j
                ctCons.target_space = 'LOCAL'
                ctCons.owner_space = 'LOCAL'
#                ctCons.use_offset = True



                ctCons =o.pose.bones[j].constraints.new("STRETCH_TO")
                ctCons.target = rootArm
                ctCons.subtarget=pointNames[i+1]
                ctCons.rest_length = lll

        bpy.ops.object.mode_set(mode='OBJECT')
        o.parent = rootArm

        o.hide_viewport = True
        

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active=rootArm
        bpy.ops.object.select_pattern(pattern=rootArm.name,extend=True)
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
NbCurveLatticeOperator,
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






