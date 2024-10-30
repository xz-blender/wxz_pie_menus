import bpy
import bmesh
import mathutils
from mathutils import Vector
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

def get_or_create_armature(name, location):
    selected_armature = next((obj for obj in bpy.context.selected_objects if obj.type == 'ARMATURE'), None)
    
    if selected_armature:
        return selected_armature
    else:
        armature = bpy.data.armatures.new(name)
        armature_object = bpy.data.objects.new(name, armature)
        bpy.context.scene.collection.objects.link(armature_object)
        armature_object.location = location
        return armature_object

def create_bone_chain(armature_object, points, stroke_index, base_name="Bone"):
    bpy.context.view_layer.objects.active = armature_object
    bpy.ops.object.mode_set(mode='EDIT')
    
    side = "L" if points[0].x <= points[-1].x else "R"
    
    bones = []
    for i in range(0,len(points) - 1,6):
        bone = armature_object.data.edit_bones.new(f"{side}_Stroke{stroke_index+1}_{base_name}_{i+1}")
        bone.head = points[i]
        bone.tail = points[i+6]
        if i > 0:
            bone.parent = bones[i-1]
            bone.use_connect = True
        bones.append(bone)
    
#    bpy.ops.object.mode_set(mode='OBJECT')
#    print(bones[0].name)
    return bones[0].name

def create_bones_for_strokes(gp_object, resampled_strokes):
    armature_name = f"{gp_object.name}_Armature"
    o =armature_object = get_or_create_armature(armature_name, gp_object.location)
    selBoneName_s =[]
    directionH_s =[]
    directionT_s =[]
    for stroke_index, stroke_points in enumerate(resampled_strokes):
        print(stroke_points)
        bone=create_bone_chain(armature_object,stroke_points,stroke_index)
        selBoneName_s.append(bone)
        directionH_s.append(stroke_points[0]-stroke_points[1])
        directionT_s.append(stroke_points[-2]-stroke_points[-1])
           
 ############  
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    bpy.context.view_layer.update()
    arm =o.data

    bpy.context.view_layer.objects.active=o
    
    arm.display_type = 'BBONE'

#    cbs=bpy.data.objects.new("NB",None)
#    cbs.empty_display_type = 'SPHERE'
    
    mesh = bpy.data.meshes.new('CBS_Cube')
    cbs = bpy.data.objects.new("Basic_Cube", mesh)
    #bpy.context.collection.objects.link(basic_sphere)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm,size=1.0)
    bm.to_mesh(mesh)
    bm.free()

    
    
    bpy.ops.object.mode_set(mode='POSE')
    
    
    bpy.ops.object.mode_set(mode='EDIT')  
    bpy.context.view_layer.update()
    for index,i in enumerate(selBoneName_s):
        bpy.context.view_layer.update()
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
#        
        bon_dir=(bone1.head-bone1.tail).normalized()
        bon_len=(bone1.head-bone1.tail).length
        
        bone_t_name =adv_rename(bone1.name,"_t_Ctrl")
        bone1t =arm.edit_bones.new(bone_t_name)#尾部新建个骨骼
        if bpy.app.version[0]==3:
            bone1t.layers[8] = True
            bone1t.layers[1] = True

        bone1t.head =bone1.tail
        bone1t.tail =bone1.tail-directionT_s[index].normalized()*bon_len*0.1
        bone1t.use_deform = False


        bone_h_name =adv_rename(bone1.name,"_h_Ctrl")
        bone1h =arm.edit_bones.new(bone_h_name)#头部新建个骨骼
        bone1h.parent = bone1.parent
        if bpy.app.version[0]==3:
            bone1h.layers[8] = True
            bone1h.layers[1] = True

        bone1h.head =bone1.head
        bone1h.tail =bone1.head-directionH_s[index].normalized()*bon_len*0.1
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
    bpy.ops.object.mode_set(mode='POSE')
     ############  
    return armature_object

def duplicate_gpencil_object(obj):
    new_gp = bpy.data.grease_pencils.new(f"{obj.name}_Copy")
    new_obj = bpy.data.objects.new(f"{obj.name}_Copy", new_gp)
    
    new_obj.matrix_world = obj.matrix_world.copy()
    
    for layer in obj.data.layers:
        new_layer = new_gp.layers.new(layer.info)
        for frame in layer.frames:
            new_frame = new_layer.frames.new(frame.frame_number)
            for stroke in frame.strokes:
                new_stroke = new_frame.strokes.new()
                new_stroke.points.add(len(stroke.points))
                for i, point in enumerate(stroke.points):
                    new_stroke.points[i].co = point.co.copy()
                    new_stroke.points[i].pressure = point.pressure
                    new_stroke.points[i].strength = point.strength
                new_stroke.line_width = stroke.line_width
                new_stroke.material_index = stroke.material_index
    
    bpy.context.scene.collection.objects.link(new_obj)
    
    return new_obj

def resample_grease_pencil_strokes(gp_object, target_point_count=6):
    all_resampled_strokes = []
    
    for layer in gp_object.data.layers:
        for frame in layer.frames:
            for stroke in frame.strokes:
                original_points = [gp_object.matrix_world @ point.co for point in stroke.points]
                
                total_length = sum((original_points[i] - original_points[i-1]).length for i in range(1, len(original_points)))
                
                segment_length = total_length / (target_point_count)
                
                new_points = [original_points[0]]
                current_length = 0
                current_index = 0
                
                for i in range(1, target_point_count):
                    target_length = i * segment_length
                    while current_length < target_length and current_index < len(original_points) - 1:
                        current_index += 1
                        current_length += (original_points[current_index] - original_points[current_index-1]).length
                    
                    if current_index == len(original_points) - 1:
                        t = 1
                    else:
                        t = (target_length - (current_length - (original_points[current_index] - original_points[current_index-1]).length)) / (original_points[current_index] - original_points[current_index-1]).length
                    
                    new_point = original_points[current_index-1].lerp(original_points[current_index], t)
                    new_points.append(new_point)
                
                new_points.append(original_points[-1])
                
                if len(stroke.points) > len(new_points):
                    for i in range(len(stroke.points) - 1, len(new_points) - 1, -1):
                        stroke.points.pop()
                elif len(stroke.points) < len(new_points):
                    for i in range(len(new_points) - len(stroke.points)):
                        stroke.points.add(1)
                
                for i, point in enumerate(new_points):
                    stroke.points[i].co = gp_object.matrix_world.inverted() @ point
                
                all_resampled_strokes.append(new_points)
    
    bpy.context.view_layer.update()
    return all_resampled_strokes

def delete_object(obj):
    bpy.data.objects.remove(obj, do_unlink=True)
    
def apply_transform_gpencil(grease_pencil_obj):
    if grease_pencil_obj.type == 'GPENCIL':
        # 计算物体的变换矩阵（世界矩阵）
        world_matrix = grease_pencil_obj.matrix_world.copy()
        
        # 遍历 Grease Pencil 图层和帧
        for layer in grease_pencil_obj.data.layers:
            for frame in layer.frames:
                for stroke in frame.strokes:
                    for point in stroke.points:
                        # 将每个点的位置从本地空间转换到世界空间
                        point.co = world_matrix @ point.co

        # 重置物体的变换矩阵为单位矩阵
        grease_pencil_obj.matrix_world = mathutils.Matrix.Identity(4)

class OBJECT_OT_grease_pencil_to_bbone_ctrl(bpy.types.Operator):
    bl_idname = "object.grease_pencil_to_bbone_ctrl"
    bl_label = "Grease Pencil to bbone_ctrl"
    bl_options = {'REGISTER', 'UNDO'}
    
   
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'GPENCIL'
    
    def execute(self, context):
        gp_object = context.active_object
        
        if gp_object and gp_object.type == 'GPENCIL':
            # 删除已存在的同名armature（如果有）
            existing_armature = bpy.data.objects.get(f"{gp_object.name}_Armature")
            if existing_armature:
                bpy.data.objects.remove(existing_armature, do_unlink=True)
            
            gp_copy = duplicate_gpencil_object(gp_object)
            
            apply_transform_gpencil(gp_copy)
            
            resampled_strokes = resample_grease_pencil_strokes(gp_copy, 6)
            
            create_bones_for_strokes(gp_copy, resampled_strokes)
       
            
            
            delete_object(gp_copy)
            
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No Grease Pencil object selected.")
            return {'CANCELLED'}

#def menu_func(self, context):
#    self.layout.operator(OBJECT_OT_grease_pencil_to_bbone_ctrl.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_grease_pencil_to_bbone_ctrl)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_grease_pencil_to_bbone_ctrl)


if __name__ == "__main__":
    register()