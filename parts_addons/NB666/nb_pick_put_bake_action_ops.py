import bpy



class NB_Pick_Put_Bake_Action_Operator(bpy.types.Operator):
    bl_idname = "object.pick_put_bake_action"
    bl_label = "拿起放下动画烘焙"
    bl_description = "拿起放下动画烘焙"
    bl_options ={"REGISTER","UNDO"}
    

    @classmethod
    def poll(cls, context):
        a=0
        if context.active_object != None:
            if context.active_object.type == 'ARMATURE':
                if context.mode == 'POSE':
                    if len(context.selected_pose_bones)>1:
                        a=1
        return a

    def draw(self,context):
        self.layout.label(text ="拿起放下动画烘焙")
        layout = self.layout  
        box = layout.box()
        row = box.row(align=True)
       
        
    def execute(self, context):
        def find_and_sort_markers():
            scene = bpy.context.scene
            markers = []

            # 遍历所有标记
            for marker in scene.timeline_markers:
                # 检查标记名称是否为"0"或"1"
                if marker.name in ["0", "1"]:
                    markers.append(marker)

            # 按帧数排序标记
            sorted_markers = sorted(markers, key=lambda m: m.frame)

            return sorted_markers


        found_markers = find_and_sort_markers()


        allname =""
        allframe =[]
        for i in found_markers:
            allname+=i.name
            allframe.append(i.frame)
            
        def split_binary_string_with_index_list(binary_string):
            substrings = []
            indices = []
            current_substring = ''
            start_index = -1
            
            for i, bit in enumerate(binary_string):
                if bit == '1' and not current_substring:
                    current_substring = '1'
                    start_index = i
                elif bit == '0' and current_substring:
                    current_substring += '0'
                    substrings.append(current_substring)
                    indices.append((start_index, i))
                    current_substring = ''
                    start_index = -1
                elif current_substring:
                    current_substring += bit
            
            # Handle the case where the string doesn't end with '0'
            if current_substring:
                substrings.append(current_substring)
                indices.append((start_index, len(binary_string) - 1))
            
            return substrings, indices


        binary_string = allname
        substrings, indices = split_binary_string_with_index_list(binary_string)

        #print("原始字符串:", binary_string)
        #print("切分结果:",substrings)
        #print("子字符串数量:", len(substrings))
        #print("索引列表:", indices)
        #print(allframe)

        active_object = bpy.context.active_object
        active_pose_bone = bpy.context.active_pose_bone
        selected_pose_bones = bpy.context.selected_pose_bones
        selected_pose_bones.remove(bpy.context.active_pose_bone)
        active_pose_bone.bone.select=False
        selected_objects=bpy.context.selected_objects

        # 获取当前场景
        current_scene = bpy.context.scene
        # 创建一个新场景
        new_scene = bpy.data.scenes.new("NBNB666")
        # 将骨架物体关联到新场景
        for obj in selected_objects: 
            new_scene.collection.objects.link(obj)
        # 切换到新场景
        bpy.context.window.scene = new_scene
        bpy.context.scene.frame_start = current_scene.frame_start
        bpy.context.scene.frame_end = current_scene.frame_end
        bpy.context.view_layer.objects.active=active_object
        for obj in selected_objects: 
            obj.select_set(True)
        for bone in selected_pose_bones: 
            bone.bone.select=True
            
        #bpy.ops.object.mode_set(mode='POSE')#切到pose模式




        def delete_keyframes_between(bone, start_frame, end_frame):  
            # 获取骨骼的动画数据
            anim_data = bone.id_data.animation_data
            if anim_data and anim_data.action:
                fcurves = anim_data.action.fcurves       
                # 遍历所有与该骨骼相关的F-Curves
                for fcurve in fcurves:
                    if bone.name in fcurve.data_path:
                        # 删除指定范围内的关键帧
                        for keyframe in reversed(fcurve.keyframe_points):
                            if start_frame < keyframe.co.x < end_frame:
                                fcurve.keyframe_points.remove(keyframe)


        # 更新视图层
        bpy.context.view_layer.update()
        for bone in selected_pose_bones:
            for i,j in enumerate(substrings):
                bpy.context.scene.frame_set(allframe[indices[i][0]])        
                print(bpy.context.scene.frame_current)
                bone.keyframe_insert(data_path="location")
                bone.keyframe_insert(data_path="rotation_euler")
                bone.keyframe_insert(data_path="rotation_quaternion")
                bone.keyframe_insert(data_path="scale")
                
                location=bone.location.copy()
                rotation_quaternion= bone.rotation_quaternion.copy()
                rotation_euler= bone.rotation_euler.copy()
                scale= bone.scale.copy()


                bpy.context.scene.frame_set(allframe[indices[i][1]])  
                
                bone.keyframe_insert(data_path="location")
                bone.keyframe_insert(data_path="rotation_euler")
                bone.keyframe_insert(data_path="scale")
                bone.location=location
                bone.rotation_quaternion= rotation_quaternion
                bone.rotation_euler=rotation_euler
                bone.scale= scale
                bone.keyframe_insert(data_path="location")
                bone.keyframe_insert(data_path="rotation_euler")
                bone.keyframe_insert(data_path="scale")
                delete_keyframes_between(bone, allframe[indices[i][0]], allframe[indices[i][1]])
                
                bpy.context.scene.frame_set(allframe[indices[i][0]])
                
                constraint = bone.constraints.new(type='CHILD_OF')
                constraint.subtarget = active_pose_bone.name
                constraint.target = active_object
                 # 设置约束空间
                constraint.target_space = 'WORLD'
                constraint.owner_space = 'WORLD'
                
                # 更新场景
                bpy.context.view_layer.update()
                
                # 设置反向矩阵以保持当前变换
                constraint.inverse_matrix = active_object.matrix_world @ active_pose_bone.matrix
                constraint.inverse_matrix.invert()


                frame_s=allframe[indices[i][0]]
                frame_e=allframe[indices[i][1]]
                if frame_e==frame_s:
                    frame_e=bpy.context.scene.frame_end
                bpy.ops.nla.bake(frame_start=frame_s, frame_end=frame_e,only_selected=True, visual_keying=True, clear_constraints=True, use_current_action=True, bake_types={'POSE'})#烘焙动画
                
        scene_to_delete = bpy.data.scenes.get("NBNB666")
        bpy.data.scenes.remove(scene_to_delete)
        bpy.context.window.scene = current_scene 
        
        bpy.ops.ed.undo_push(message="NB")
        return {"FINISHED"}

















classes=(
NB_Pick_Put_Bake_Action_Operator,
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






