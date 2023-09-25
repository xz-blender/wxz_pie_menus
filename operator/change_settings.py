import bpy
import sys

def change_preferences_settings():
    C = bpy.context
    pref = C.preferences

    # 界面
    view = pref.view
    view.text_hinting = 'FULL'  # 文本微调
    view.show_developer_ui = True   # 开发者选项
    view.show_tooltips_python = True    # Python工具提示
    view.color_picker_type = 'SQUARE_SV'    # 拾色器类型
    view.show_statusbar_memory = True    # 内存使用量
    if sys.platform == "win32":
        view.show_statusbar_vram = True     # 显存使用量
    view.show_statusbar_version = True    # 显示版本
    view.use_mouse_over_open = True     # 鼠标划过开启菜单

    from pathlib import Path
    font_path = Path(__file__).parent.parent/'ui_font.TTC'
    view.font_path_ui = str(font_path)   # 界面字体

    # 动画
    edit = pref.edit
    # edit.use_visual_keying = True       # 可视化插帧
    # edit.use_keyframe_insert_needed = True      # 仅在需要处插入关键帧

    # 输入
    inputs = pref.inputs
    inputs.use_numeric_input_advanced = True    # 启用数学表达式输入

    # 视图切换
    inputs.walk_navigation.use_gravity = True   # 启用行走重力
    inputs.walk_navigation.view_height = 1.7   # 启用行走重力
    inputs.use_mouse_depth_navigate = True      # 使用鼠标深度
    inputs.use_zoom_to_mouse = True     # 缩放至鼠标位置
    view.smooth_view = 0    # 平滑视图 0
    
    # 系统
    edit = pref.edit
    if sys.platform == "win32":
        pref.addons['cycles'].preferences.compute_device_type = 'OPTIX' # 设置渲染设备
    edit.undo_steps = 128   # 撤销次数
    
    # 保存&加载
    filepaths = pref.filepaths
    filepaths.save_version = 0  # 保存版本0
    filepaths.recent_files = 30     # 查看最近打开文件数量
    filepaths.use_file_compression = True   # 使用文件压缩
    # bpy.data.use_autopack = True

    # 主题
    theme = pref.themes[0]
    theme.node_editor.noodle_curving = 0 # 节点编辑器,曲线弯曲度

    theme.view_3d.edge_width = 3 # 3D视图,边缘宽度
    theme.view_3d.outline_width = 3 # 3D视图,轮廓宽度
    theme.view_3d.object_origin_size = 4 # 3D视图,对象原点大小

    

def change_context_settings():
    context = bpy.context
    scene = context.scene
    # -------渲染设置-------
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.cycles.preview_samples = 16 # 预览采样
    scene.cycles.samples = 1024 # 预览采样
    scene.render.film_transparent = True # 胶片透明
    scene.cycles.use_auto_tile = False # 渲染使用平铺
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'None'

    # -------3D View-------
    scene.tool_settings.snap_elements = {'VERTEX'} # 吸附到点模式

def change_settings():
    try:
        change_preferences_settings()
        change_context_settings()
        print('"WXZ_Pie_Menu" changed settings!')
    except:
        pass

def register():
    if not bpy.app.timers.is_registered(change_settings):
        bpy.app.timers.register(change_settings, first_interval=1)

def unregister(): 
    if bpy.app.timers.is_registered(change_settings):
        bpy.app.timers.unregister(change_settings)

if __name__ == "__main__":
    register()