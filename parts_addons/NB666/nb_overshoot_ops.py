import bpy
from mathutils import Vector

def bone_find_adjacent_keyframes():
    # 获取当前选择的骨骼对象
    obj = bpy.context.object
    if obj is None or obj.type != 'ARMATURE':
        return None
    
    actions = obj.animation_data.action.fcurves
    
    # 获取当前时间轴位置
    frame = bpy.context.scene.frame_current
    
    # 保存前一关键帧和后一关键帧
    prev_keyframe = None
    next_keyframe = None
    
    for fc in actions:
        if fc.data_path[0:10] =='pose.bones':
            bone_name = fc.data_path.split("\"")[1]
            bone = obj.pose.bones.get(bone_name)
            if bone is not None and bone.bone.select:
                for kp in fc.keyframe_points:
                    if kp.co.x < frame:
                        prev_keyframe = max(prev_keyframe, kp.co.x) if prev_keyframe is not None else kp.co.x
                    elif kp.co.x > frame:
                        next_keyframe = min(next_keyframe, kp.co.x) if next_keyframe is not None else kp.co.x
    
    if prev_keyframe is None:
        prev_keyframe=frame-1
    if next_keyframe is None:
        next_keyframe=frame+1
    return prev_keyframe, next_keyframe





            
def NB_Overshoot(factor=1, loc =False,rot =False,size =False, axis_lock='FREE',gap_frame =2):   
    keyframes = bone_find_adjacent_keyframes()
    prev, next = keyframes        
#    print("前一关键帧：", prev)
#    print("后一关键帧：", next)
    if loc and rot and size:
        bpy.ops.pose.push(factor=factor, prev_frame=int(prev), next_frame=int(next),channels='ALL',axis_lock=axis_lock)
    else:
        if loc:
            bpy.ops.pose.push(factor=factor, prev_frame=int(prev), next_frame=int(next),channels='LOC',axis_lock=axis_lock)
        if rot:
            bpy.ops.pose.push(factor=factor, prev_frame=int(prev), next_frame=int(next),channels='ROT',axis_lock=axis_lock)
        if size:
            bpy.ops.pose.push(factor=factor, prev_frame=int(prev), next_frame=int(next),channels='SIZE',axis_lock=axis_lock)
        pass
       
    bpy.context.scene.frame_current-=gap_frame 
    
    keyframes = bone_find_adjacent_keyframes()
    prev, next = keyframes        
    
    if loc and rot and size:
        bpy.ops.pose.push(factor=factor, prev_frame=int(prev), next_frame=int(next),channels='ALL',axis_lock=axis_lock)
    else:
        if loc:
            bpy.ops.pose.push(factor=factor, prev_frame=int(prev), next_frame=int(next),channels='LOC',axis_lock=axis_lock)
        if rot:
            bpy.ops.pose.push(factor=factor, prev_frame=int(prev), next_frame=int(next),channels='ROT',axis_lock=axis_lock)
        if size:
            bpy.ops.pose.push(factor=factor, prev_frame=int(prev), next_frame=int(next),channels='SIZE',axis_lock=axis_lock)
        pass
    bpy.context.scene.frame_current+=gap_frame *2









class NB_AN_overshoot(bpy.types.Operator):
    bl_idname = "nb_anima.overshoot"
    bl_label = "Overshoot"
    bl_description = "Overshoottttt"


    @classmethod
    def poll(cls, context: bpy.types.Context):
        a=0
        if context.active_object != None:
            if context.active_object.type == 'ARMATURE':
                if context.mode == 'POSE':
                    if len(context.selected_pose_bones)>0:
                        if context.active_object.animation_data != None:
                            if context.active_object.animation_data.action != None:
                                a=1
        return a

    def execute(self, context: bpy.types.Context):
        
        rest_frame_current=bpy.context.scene.frame_current
        rest_auto_key=bpy.context.scene.tool_settings.use_keyframe_insert_auto
        bpy.context.scene.tool_settings.use_keyframe_insert_auto=True
        
        gap_frame=bpy.context.scene.Prop_nb_666.gap_frame
        bpy.context.scene.frame_current+=gap_frame
        
        loc =bpy.context.scene.Prop_nb_666.LOC
        rot =bpy.context.scene.Prop_nb_666.ROT
        size=bpy.context.scene.Prop_nb_666.SIZE
        
        cycle_index=bpy.context.scene.Prop_nb_666.cycle_index
        factor=bpy.context.scene.Prop_nb_666.factor
        
        for i in range(cycle_index):
            NB_Overshoot(factor=factor,gap_frame=gap_frame,loc =loc,rot =rot,size=size,axis_lock='FREE')
            
        bpy.context.scene.tool_settings.use_keyframe_insert_auto=rest_auto_key
        bpy.context.scene.frame_current=rest_frame_current
        
        bpy.ops.ed.undo_push(message="NB")              
        return {"FINISHED"}


# ---------REGISTER ----------.

classes = (
    NB_AN_overshoot,
    # 添加其他需要注册的操作符类...
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
