import bpy
import math 
import bmesh
import mathutils 


class NB_TrackOffset_BoneChain_Operator(bpy.types.Operator):
    bl_idname = "nb_frame.track_offset_bonechain"
    bl_label = "骨骼链跟随错帧"
    bl_description = "点他牛逼的骨骼链跟随错帧"

    @classmethod
    def poll(cls, context):
        a=0
        if context.active_object != None:
            if context.active_object.type == 'ARMATURE':
                if context.mode == 'POSE':
                    if len(context.selected_pose_bones)>0:
                        a=1
        return a

    def execute(self, context):
                
        #import mathutils
        C = bpy.context
        Armature =C.object
        #bone =C.active_pose_bone#获取激活骨骼
        bone =C.selected_pose_bones[0]#获取选择骨骼
        
        cInfluence=bpy.context.scene.Prop_nb_666.cInfluence
        cuoFrame=bpy.context.scene.Prop_nb_666.cuoFrame
        velocity_weight=bpy.context.scene.Prop_nb_666.velocity_weight
        
        
         # 获取当前场景
        current_scene = bpy.context.scene
        # 创建一个新场景
        new_scene = bpy.data.scenes.new("NBNB666")
        # 将骨架物体关联到新场景
        new_scene.collection.objects.link(Armature)
        # 切换到新场景
        bpy.context.window.scene = new_scene
        bpy.context.scene.frame_start = current_scene.frame_start
        bpy.context.scene.frame_end = current_scene.frame_end
        C.view_layer.objects.active=Armature
        bpy.context.active_object.select_set(True)#设置激活和选择物体为骨架
        bpy.ops.object.mode_set(mode='POSE')#切到pose模式
        
#        # 遍历骨架对象的所有子对象
#        originalshow_viewport=[]
#        originalshow_render=[]
#        originalmodifiers=[]
#        for child_obj in Armature.children:
#            # 检查子对象是否是 mesh 并且是否受到骨骼影响
#            if child_obj.type == 'MESH' and child_obj.find_armature() == Armature:
#                for i in child_obj.modifiers:
#                    originalmodifiers.append(i)
#                    originalshow_viewport.append(i.show_viewport)
#                    originalshow_render.append(i.show_render)
#                    i.show_viewport = False
#                    i.show_render = False
#        

        def genSuiCuoZhen(Abone,gensuiAmp =1):
            #####
            consSS =Abone.constraints[:]
            propDirS =[]
            propAttrS=[]
            typeS=[]
            for con in consSS:
                propDir  =dir(con)
                propAttr =[]
                for prop in dir(con):
                    propAttr.append(getattr(con,prop))
                
                propDirS.append(propDir)
                propAttrS.append(propAttr)
                typeS.append(con.type)
           ###### 
            emp=bpy.data.objects.new("NB",None)#建个空物体
            emp.empty_display_type = 'PLAIN_AXES'
            bpy.context.scene.collection.objects.link(emp)
            cons =emp.constraints.new('COPY_LOCATION')#空物体添加个位置约束
            cons.target =Armature
            cons.subtarget =Abone.name
            cons.head_tail =1

            bpy.ops.object.mode_set(mode='OBJECT')#切到物体模式
            bpy.ops.object.select_all(action='DESELECT')#全部取消选择

            C.view_layer.objects.active=emp#设置激活和选择物体为空物体
            C.active_object.select_set(True)

            # 获取所有的 actions
            orig_action=[]
            for action in bpy.data.actions:
                orig_action.append(action)


            sce = bpy.context.scene
            bpy.ops.nla.bake(frame_start=sce.frame_start-1, frame_end=sce.frame_end+1,only_selected=True, visual_keying=True, clear_constraints=True, use_current_action=True,bake_types={'OBJECT'})#烘焙动画
            #下面这一串是错帧用的
            val = cuoFrame
            sel = [o for o in bpy.context.selected_objects if o.animation_data]

            for obj in sel:
                act = obj.animation_data.action
                for fcu in act.fcurves:
                    for kp in fcu.keyframe_points: 
                        kp.co[0] +=  val
                        kp.handle_left[0] += val
                        kp.handle_right[0] += val

            bonecons =Abone.constraints.new('DAMPED_TRACK')#给骨骼添加一个阻尼跟随约束
            bonecons.target = emp
            bonecons.influence = gensuiAmp#约束影响强度（要拿出来调的）

       #############################vel########vel########vel################################# 
            frame_start = bpy.context.scene.frame_start
            frame_end = bpy.context.scene.frame_end

            velocities = []
            # 遍历所有帧
            frame_current=bpy.context.scene.frame_current
            for frame in range(frame_start, frame_end):
                bpy.context.scene.frame_set(frame)
                pos1 = Abone.head.copy()               
                bpy.context.scene.frame_set(frame + 1)
                pos2 = Abone.head.copy()
                
                # 计算位置变化
                distance = (pos2 - pos1).length
                velocities.append(distance)
            
            Velocity_weight =velocity_weight
            for frame in range(frame_start, frame_end):
                bpy.context.scene.frame_set(frame)
                bonecons.influence = (velocities[bpy.context.scene.frame_current-frame_start]/max(max(velocities),0.001)*Velocity_weight+(1-Velocity_weight))*gensuiAmp
                bonecons.keyframe_insert(data_path="influence", frame=frame)
                
            bpy.context.scene.frame_set(frame_current)
#############################vel########vel########vel################################# 


            bpy.ops.object.select_all(action='DESELECT')#全部取消选择

            C.view_layer.objects.active=Armature
            C.active_object.select_set(True)#设置激活和选择物体为骨架

            bpy.ops.object.mode_set(mode='POSE')#切到pose模式
            
            bpy.ops.pose.select_all(action='DESELECT')
                 
            bpy.context.object.data.bones.active = Abone.bone#设置激活骨骼

            bpy.ops.nla.bake(frame_start=sce.frame_start-1, frame_end=sce.frame_end+1, only_selected=True, visual_keying=True, clear_constraints=True, use_current_action=True, bake_types={'POSE'})#烘焙动画

            bpy.data.objects.remove(emp)#删除空物体
            
            ###################清除骨骼约束上的动画数据（速度强度）###############
            # 获取当前场景中的动作数据
            action = bpy.context.object.animation_data.action

            # 遍历选中的骨骼
            for bone in bpy.context.selected_pose_bones:
                constraints_names = [constraint.name for constraint in bone.constraints]
                
                # 遍历动作中的所有 fcurve
                for fc in action.fcurves:
                    # 查找与骨骼约束相关的 fcurves
                    if fc.data_path.startswith(f'pose.bones["{bone.name}"].constraints'):
                        # 获取路径中约束的名称
                        constraint_name = fc.data_path.split('"')[3]
                        
                        # 如果该约束已经被删除，不在当前约束列表中，则删除该 fcurve
                        if constraint_name not in constraints_names:
                            action.fcurves.remove(fc)
                            
            #################
            
            
            # 获取所有的 actions
            for action in bpy.data.actions:
                # 检查 action 是否有用户
                if action.users == 0 and action not in orig_action:
                    # 没有用户，删除该 action
                    bpy.data.actions.remove(action)
            
            

            
            #####
            for n in range(len(consSS)):
                # 创建一个新的约束实例
                new_constraint = Abone.constraints.new(typeS[n])
                # 逐一复制属性
                for i,prop in enumerate(dir(new_constraint)):
                    if not prop.startswith("_"):
                        try:
                            setattr(new_constraint, prop, propAttrS[n][i])
                        except:
                            pass
          ########


        def s_node(Abone,gensuiAmp):   #递归骨骼链
        #    gensuiAmp=gensuiAmp
            genSuiCuoZhen(Abone,gensuiAmp)
            if Abone.child !=None:       
                Abone=Abone.child
                s_node(Abone,gensuiAmp)
 

        selboneS=C.selected_pose_bones
#        genSuiCuoZhen(bone,bpy.context.scene.Prop_nb_666.cInfluence)
#        weiZHCuoZhen(bone,bpy.context.scene.Prop_nb_666.cInfluence)
        s_node(bone,cInfluence)  
        
        for i in selboneS: 
            bpy.context.object.data.bones[i.name].select=1   
        
#        for i,mod in enumerate(originalmodifiers):
#            mod.show_viewport=originalshow_viewport[i]
#            mod.show_render=originalshow_render[i]

        scene_to_delete = bpy.data.scenes.get("NBNB666")
        bpy.data.scenes.remove(scene_to_delete)
        bpy.context.window.scene = current_scene
        
        bpy.ops.ed.undo_push(message="NB") 
        return {"FINISHED"}
    














classes=(
NB_TrackOffset_BoneChain_Operator,
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






