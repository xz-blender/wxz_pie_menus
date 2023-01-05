import bpy
import sys

def change_preferences_settings():
    C = bpy.context
    pref = C.prefrences

    # 界面
    view = pref.view
    view.show_developer_ui = True   # 开发者选项
    view.show_tooltips_python = True    # Python工具提示
    view.color_picker_type = 'SQUARE_SV'    # 拾色器类型
    view.statusbar_memory = True    # 内存使用量
    if sys.platform == "win32":
        view.show_statusbar_vram = True     # 显存使用量
    view.statusbar_version = True    # 显示版本
    view.use_mouse_over_open = True     # 鼠标划过开启菜单

    # 动画
    edit = pref.edit
    edit.use_visual_keying = True       # 可视化插帧
    edit.use_keyframe_insert_needed = True      # 仅在需要处插入关键帧

    # 输入
    inputs = pref.inputs
    inputs.use_numeric_input_advanced = True    # 启用数学表达式输入
    

    

def register():
    if not bpy.app.timers.is_registered(change_preferences_settings):
        bpy.app.timers.register(change_preferences_settings, first_interval=5)


def unregister(): 
    if bpy.app.timers.is_registered(change_preferences_settings):
        bpy.app.timers.unregister(change_preferences_settings)

if __name__ == "__main__":
    register()