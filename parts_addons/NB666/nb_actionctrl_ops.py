import bpy
import math 
import bmesh
import mathutils 

class NB_actionctrl_Operator(bpy.types.Operator):
    """快速添加动作约束用的 姿态模式下选择有动画的骨骼 再加选控制器骨骼 """
    bl_idname = "object.nbactionctrloperator"
    bl_label = "nb add action ctrl"
    
    my_enum: bpy.props.EnumProperty(
        name="Channel",
        description="Select an option",
        items=[
            ('LOCATION_X', "X Location", "Description X"),
            ('LOCATION_Y', "Y Location", "Description Y"),
            ('LOCATION_Z', "Z Location", "Description Z"),
        ],
        default='LOCATION_Y',
    )
    
    negative_bool: bpy.props.BoolProperty(
        name="-负方向",
        description="-负方向",
        default=False,
    )
    middle_bool: bpy.props.BoolProperty(
        name="中间",
        description="middle",
        default=False,
    )
    
    def invoke(self, context,event):
        wm =context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Target")
        column = layout.column()

        row = column.row(align=True)
        row.prop(self, "negative_bool")
        row.prop(self, "my_enum")
        row.prop(self, "middle_bool")
        
    @classmethod
    def poll(cls, context):
        a=0

        if context.active_object != None:
            if context.active_object.type == 'ARMATURE':
                if context.mode == 'POSE':
                    if len(context.selected_pose_bones)>1:
                        a=1
        return a

    def execute(self, context):
                # 获取选中的对象
        selected_objects = bpy.context.selected_objects

        # 获取激活的对象（假设你只激活了一个对象）
        active_object = bpy.context.active_object

        selected_pose_bones = [bone for bone in active_object.data.bones if bone.select]


        # 检查对象是否有动画数据
        if active_object.animation_data:            
            # 获取当前激活的动作
            active_action = active_object.animation_data.action
            if active_action:
                if len(active_action.fcurves[:])>0:
                    # 初始化帧范围的上下限
                    start_frame = end_frame = None

                    # 遍历所有 fcurves
                    for fcurve in active_action.fcurves:
                        for keyframe in fcurve.keyframe_points:
                            frame = keyframe.co[0]

                            # 更新帧范围的上下限
                            if start_frame is None or frame < start_frame:
                                start_frame = frame
                            if end_frame is None or frame > end_frame:
                                end_frame = frame
                                
                    if end_frame>start_frame:
                        # 定义目标方向（例如，世界坐标系中的上方向，即 Z 轴方向）
                        target_direction = mathutils.Vector((0, 0, 1))

                        # 定义对象的局部方向（例如，Y 轴方向）
                        if self.my_enum =='LOCATION_X':
                            local_direction = mathutils.Vector((1 if self.negative_bool else -1, 0, 0))
                        if self.my_enum =='LOCATION_Y':
                            local_direction = mathutils.Vector((0, 1 if self.negative_bool else -1, 0))
                        if self.my_enum =='LOCATION_Z':
                            local_direction = mathutils.Vector((0, 0, -1 if self.negative_bool else 1))

                        # 计算旋转矩阵，将 local_direction 旋转到 target_direction
                        rotation_matrix = local_direction.rotation_difference(target_direction).to_matrix().to_4x4()

                        # 创建一个新的网格对象
                        
                        mesh = bpy.data.meshes.new('ConeMesh')
                        CBS_Cone = bpy.data.objects.new("CBS_Cone", mesh)
                        bm = bmesh.new()
                        bmesh.ops.create_cone(
    bm,
    cap_ends=True,        # 创建底部和顶部的封盖
    cap_tris=False,       # 不将封盖三角化
    segments=4,          # 底部的分段数
    radius1=0.25,          # 底部半径
    radius2=0.2 if self.middle_bool else 0.0,          # 顶部半径（0 表示一个尖顶的圆锥）
    depth=1.0,            # 圆锥体的高度
    matrix=rotation_matrix # 使用旋转矩阵设置圆锥体的方向
)
                        bm.to_mesh(mesh)
                        bm.free()
                        
                        active_action.use_fake_user = True
                        active_object.animation_data.action=None
                        
                        active_bone_length=bpy.context.active_pose_bone.length
                        for i,pose_bone in enumerate(selected_pose_bones):

                            # 在选中的pose_bone上添加Copy Transforms约束
                            if pose_bone.name != bpy.context.active_pose_bone.name :
                                copy_transforms_constraint = active_object.pose.bones[pose_bone.name].constraints.new(type='ACTION')
                                copy_transforms_constraint.subtarget = bpy.context.active_pose_bone.name
                                copy_transforms_constraint.target = active_object
                                copy_transforms_constraint.transform_channel = self.my_enum
                                copy_transforms_constraint.target_space = 'LOCAL'
                                copy_transforms_constraint.max = -active_bone_length if self.negative_bool else active_bone_length
                                if self.middle_bool:
                                    copy_transforms_constraint.min = active_bone_length/2 if self.negative_bool else -active_bone_length/2

                                    copy_transforms_constraint.max = -active_bone_length/2 if self.negative_bool else active_bone_length/2



                                copy_transforms_constraint.action = active_action
                                copy_transforms_constraint.frame_start = int(start_frame)
                                copy_transforms_constraint.frame_end = int(end_frame)
                                
                                pose_bone.select = False
                                active_object.pose.bones[pose_bone.name].location[0]=0
                                active_object.pose.bones[pose_bone.name].location[1]=0
                                active_object.pose.bones[pose_bone.name].location[2]=0
                                active_object.pose.bones[pose_bone.name].rotation_quaternion[0] = 1
                                active_object.pose.bones[pose_bone.name].rotation_quaternion[1] = 0
                                active_object.pose.bones[pose_bone.name].rotation_quaternion[2] = 0
                                active_object.pose.bones[pose_bone.name].rotation_quaternion[3] = 0
                                active_object.pose.bones[pose_bone.name].rotation_euler[0] = 0
                                active_object.pose.bones[pose_bone.name].rotation_euler[1] = 0
                                active_object.pose.bones[pose_bone.name].rotation_euler[2] = 0
                                active_object.pose.bones[pose_bone.name].scale[0]=1
                                active_object.pose.bones[pose_bone.name].scale[1]=1
                                active_object.pose.bones[pose_bone.name].scale[2]=1

                                
                        bpy.context.active_pose_bone.custom_shape = CBS_Cone           
                  


                    else:
                        self.report({'INFO'}, "动画至少两帧")  
                else:
                    self.report({'INFO'}, "没帧")  
            else:
                self.report({'INFO'}, "No Action 没动作") 
        else:
            self.report({'INFO'}, "没动画数据 No animation data") 

                
                
        bpy.ops.ed.undo_push(message="NB")       
        return {'FINISHED'}




classes=(
NB_actionctrl_Operator,
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






