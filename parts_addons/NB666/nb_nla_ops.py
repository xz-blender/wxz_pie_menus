import bpy
import datetime
import os
import math
import tempfile

# 获取临时文件夹路径
#temp_folder = bpy.path.abspath('//temp')
temp_folder =tempfile.gettempdir()
# 如果临时文件夹不存在，则创建它
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

# 创建一个文本文件来保存时间线数据
output_file = os.path.join(temp_folder, 'timeline_data.txt')

# 记录状态的标志
recording = False

# 保存原始的边框颜色
original_border_color = bpy.context.preferences.themes[0].view_3d.space.header[:]


def record_timeline_handler(scene):
    global recording
    
    if recording:
        frame = scene.frame_current
    
#        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        current_time = datetime.datetime.now().strftime("%S%f")
        # 写入数据到文件
        with open(output_file, 'a') as file:
            file.write(f"{frame}\t{current_time}\n")

            # 在每次记录时改变3D视图的边框颜色
#            bpy.context.preferences.themes[0].view_3d.space.header = (1.0, 0.0, 0.0, 1.0)  # 设置为红色

def toggle_record_timeline(self, context):
    global recording
    orig_cframe =bpy.context.scene.frame_current
    # 切换记录状态
    recording = not recording

    if recording:
        # 清空文件
        with open(output_file, 'w'):
            pass
        bpy.context.preferences.themes[0].view_3d.space.header = (1.0, 0.0, 0.0, 1.0)  # 设置为红色
        # 启动帧变化后的处理程序
        bpy.app.handlers.frame_change_post.append(record_timeline_handler)

    else:
        # 停止帧变化后的处理程序
        bpy.app.handlers.frame_change_post.remove(record_timeline_handler)

        # 恢复边框颜色
        bpy.context.preferences.themes[0].view_3d.space.header = original_border_color
        
        bpy.ops.screen.animation_cancel(restore_frame=False)
        
        scene = bpy.context.scene

        # 获取渲染相关的信息
        render = bpy.context.scene.render
        fps = render.fps
        fps_base = render.fps_base

        # 计算帧率
        frame_rate = fps / fps_base
        # 获取场景中的所有非线性动画片段
        nla_strips = []

        for obj in scene.objects:
            if obj.animation_data and obj.animation_data.nla_tracks:
                for track in obj.animation_data.nla_tracks:
                    nla_strips.extend(track.strips)


        

        kFrames=[]
        rTimes=[]
        # 打开文件
        with open(output_file, 'r', encoding='utf-8') as file:
            # 逐行读取文档
            for line in file:
                # 做一些处理，比如打印每行内容
                kFrames.append(float(line.strip().split("\t")[0]))
                rTimes.append(float(line.strip().split("\t")[1]))
#        print(kFrames)
#        print(rTimes)


        scene.frame_current=orig_cframe 
        # 遍历所有非线性动画片段
        for strip in nla_strips:
            # 检查片段是否激活
            if strip.active:
                strip.use_animated_time = True
                
                b =0
                for i,k in enumerate(kFrames):            
                    strip.strip_time = k
                    strip.keyframe_insert("strip_time")
                    if i>1:
                        a=(rTimes[i]-rTimes[i-1])/(1000000/frame_rate)  
                        a=max(a,0)
                        if a <0.5:
                            b+=a
                            if b > 0.5:
                                b=0
                                scene.frame_current+=1
                        scene.frame_current+=round(a)
                       
#                        print(a)
                    
                    
                strip.frame_end_ui = scene.frame_current

            
#                print("当前激活的非线性动画片段：", strip.name)
                
       
# 注册操作员和菜单项
class RecordTimelineOperator(bpy.types.Operator):
    bl_idname = "wm.record_timeline"
    bl_label = "Record Timeline"

    def execute(self, context):
        toggle_record_timeline(self, context)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(RecordTimelineOperator.bl_idname)

def register():
    bpy.utils.register_class(RecordTimelineOperator)
    bpy.types.NLA_MT_editor_menus.append(menu_func)

def unregister():
    bpy.utils.unregister_class(RecordTimelineOperator)
    bpy.types.NLA_MT_editor_menus.remove(menu_func)

if __name__ == "__main__":
    register()
