import bpy
import sys

def change_preferences_settings():
    C = bpy.context
    pref = C.preferences
    cycles = C.scene.cycles

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
    font_path = Path(__file__).parent.parent/'ui_font.ttf'
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
    if sys.platform == "win32":
        pref.addons['cycles'].preferences.compute_device_type = 'OPTIX' # 设置渲染设备
        cycles.preview_denoiser = "OPTIX"   # 预览降噪设备
        cycles.denoiser = "OPTIX"   # 渲染降噪设备
    elif sys.platform == "darwin":
        pref.addons['cycles'].preferences.compute_device_type = 'METAL' # 设置渲染设备
        cycles.preview_denoiser = "AUTO"   # 预览降噪设备
        cycles.denoiser = 'OPENIMAGEDENOISE'   # 渲染降噪设备
        
    edit = pref.edit
    edit.undo_steps = 128   # 撤销次数

    # 保存&加载
    filepaths = pref.filepaths
    filepaths.save_version = 0  # 保存版本0
    filepaths.recent_files = 30     # 查看最近打开文件数量
    filepaths.use_file_compression = True   # 使用文件压缩
    # bpy.data.use_autopack = True

    # 主题
    theme = pref.themes[0]
    theme.node_editor.noodle_curving = 3 # 节点编辑器,曲线弯曲度
    #  ----3D视图
    theme.view_3d.edge_width = 5 # 边缘宽度
    theme.view_3d.gp_vertex_size = 6 # 蜡笔顶点尺寸
    theme.view_3d.vertex_size = 5 # 顶点尺寸
    theme.view_3d.edge_width = 5 # 面的点尺寸
    theme.view_3d.outline_width = 3 # 轮廓宽度
    theme.view_3d.object_origin_size = 7 #对象原点大小

    

def change_context_settings():
    context = bpy.context
    scene = context.scene
    cycles = scene.cycles
    render = scene.render
    v_sets = scene.view_settings
    # -------渲染设置-------

    render.engine = 'CYCLES'
    cycles.device = 'GPU'

    cycles.use_preview_denoising = True #预览采样开关
    cycles.use_denoising = True #渲染采样开关
    cycles.use_guiding = True #灯光树开关
    cycles.use_light_tree = True #灯光树
    cycles.use_volume_guiding = True #灯光树-体积采样开关
    cycles.preview_denoising_start_sample = 4 # 预览降噪-起始采样
    cycles.preview_denoising_input_passes = "RGB_ALBEDO_NORMAL" # 预览降噪-通道选择
    cycles.denoising_input_passes = "RGB_ALBEDO_NORMAL" # 渲染降噪-通道选择
    cycles.preview_denoising_use_gpu = True # 预览降噪-使用GPU
    cycles.denoising_use_gpu = True # 渲染降噪-使用GPU

    cycles.preview_samples = 16 # 预览采样
    cycles.samples = 1024 # 预览采样
    cycles.use_auto_tile = False # 渲染使用平铺
    v_sets.view_transform = 'AgX'
    v_sets.look = 'None'
    render.film_transparent = True # 胶片透明

    scene.cycles.max_bounces = 16
    scene.cycles.diffuse_bounces = 16
    scene.cycles.diffuse_bounces = 16
    scene.cycles.glossy_bounces = 16
    scene.cycles.transmission_bounces = 16
    scene.cycles.volume_bounces = 0
    scene.cycles.transparent_max_bounces = 16
    scene.cycles.caustics_reflective = False
    scene.cycles.caustics_refractive = False

    # -------3D View-------
    scene.transform_orientation_slots[0].type = 'GLOBAL' # 变换轴方向
    scene.tool_settings.transform_pivot_point = 'BOUNDING_BOX_CENTER' # 变换中心点
    # 吸附到点模式
    scene.tool_settings.snap_elements_base = {'FACE', 'EDGE_MIDPOINT', 'VERTEX', 'EDGE', 'EDGE_PERPENDICULAR'}

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