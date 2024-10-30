import bpy
import bmesh
import mathutils
from mathutils import Vector

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
    for i in range(len(points) - 1):
        bone = armature_object.data.edit_bones.new(f"{side}_Stroke{stroke_index+1}_{base_name}_{i+1}")
        bone.head = points[i]
        bone.tail = points[i+1]
        if i > 0:
            bone.parent = bones[i-1]
            bone.use_connect = True
        bones.append(bone)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return bones

def create_bones_for_strokes(gp_object, resampled_strokes):
    armature_name = f"{gp_object.name}_Armature"
    armature_object = get_or_create_armature(armature_name, gp_object.location)
    
    for stroke_index, stroke_points in enumerate(resampled_strokes):
        create_bone_chain(armature_object, stroke_points, stroke_index)
    
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

class OBJECT_OT_grease_pencil_to_armature(bpy.types.Operator):
    bl_idname = "object.grease_pencil_to_armature"
    bl_label = "Grease Pencil to Armature"
    bl_options = {'REGISTER', 'UNDO'}
    
    target_point_count: bpy.props.IntProperty(
        name="Bone Count",
        description="Number of points to resample each stroke to",
        default=2,
        min=1,
        max=32
    )
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'GPENCIL'
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "target_point_count")
    
    def execute(self, context):
        gp_object = context.active_object
        
        if gp_object and gp_object.type == 'GPENCIL':
            # 删除已存在的同名armature（如果有）
            existing_armature = bpy.data.objects.get(f"{gp_object.name}_Armature")
            if existing_armature:
                bpy.data.objects.remove(existing_armature, do_unlink=True)
            
            gp_copy = duplicate_gpencil_object(gp_object)
            
            apply_transform_gpencil(gp_copy)
            
            resampled_strokes = resample_grease_pencil_strokes(gp_copy, self.target_point_count)
            
            create_bones_for_strokes(gp_copy, resampled_strokes)
            
            gp_copy_name = gp_copy.name
            
            delete_object(gp_copy)
            
#            self.report({'INFO'}, f"Process completed. Armature created with {self.target_point_count} points per stroke. Grease Pencil copy '{gp_copy_name}' deleted.")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "No Grease Pencil object selected.")
            return {'CANCELLED'}

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_grease_pencil_to_armature.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_grease_pencil_to_armature)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_grease_pencil_to_armature)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
    register()