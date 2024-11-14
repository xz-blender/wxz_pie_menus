from pathlib import Path

import bpy
from bpy.types import Operator

from .items import oneclick_enable_preset_prop_list
from .utils import get_prefs, safe_register_class, safe_unregister_class

operator_folder_path = Path(__file__).parent / "operator"
assets_p_file = operator_folder_path / "assets_lib_presets.json"
addons_p_file = operator_folder_path / "addons_lib_presets.json"

p_files_dirt = {"Assets": assets_p_file, "Addons": addons_p_file}


class PIE_Open_Custom_XZ_presets_file_In_NewWindow(Operator):
    bl_idname = "pie.open_custom_xz_presets_file_in_new_window"
    bl_label = "打开预设文件"
    bl_options = {"REGISTER", "UNDO"}

    path_name: bpy.props.StringProperty()  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        file_path = Path(p_files_dirt[self.path_name])

        if not file_path.exists():
            self.report({"ERROR"}, f"预设文件 '{file_path}' 没有找到!")
            return {"CANCELLED"}
        # 检查文件是否已经加载
        text_name = file_path.name
        D_t = bpy.data.texts
        if text_name in D_t:
            text_data = D_t.get(text_name)
            text_data.use_fake_user = False
        else:
            text_data = D_t.load(str(file_path))
        # 新建一个程序窗口并设置为文本编辑器
        bpy.ops.screen.area_dupli("INVOKE_DEFAULT")
        new_area = context.screen.areas[-1]
        new_area.type = "TEXT_EDITOR"
        # 显示加载的文本文件
        new_area.spaces.active.text = text_data
        # 文本编辑器显示设置
        settings = new_area.spaces[0]
        settings.show_line_highlight = True
        settings.show_word_wrap = True

        return {"FINISHED"}


class PIE_OneClick_Enable_All_Presets(Operator):
    bl_idname = "pie.one_click_enable_all_presets"
    bl_label = "一键启用所有预设"
    bl_description = "一键启用所有预设"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="即将重启,是否执行?", icon="QUESTION")

    def execute(self, context):
        prefs = get_prefs()
        for prop in oneclick_enable_preset_prop_list:
            setattr(prefs, prop, True)
        bpy.ops.wm.save_userpref()
        bpy.ops.wm.relaunch_blender()
        return {"FINISHED"}


CLASSES = [
    PIE_Open_Custom_XZ_presets_file_In_NewWindow,
    PIE_OneClick_Enable_All_Presets,
]


def register():
    safe_register_class(CLASSES)


def unregister():
    safe_unregister_class(CLASSES)
