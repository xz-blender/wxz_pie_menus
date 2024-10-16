from pathlib import Path

import bpy

operator_folder_path = Path(__file__).parent / "operator"
assets_p_file = operator_folder_path / "assets_lib_presets.json"
addons_p_file = operator_folder_path / "addons_lib_presets.json"


class PIE_Open_Custom_XZ_presets_file_In_NewWindow(bpy.types.Operator):
    bl_idname = "pie.open_custom_xz_presets_file_in_new_window"
    bl_label = "打开预设文件"
    bl_options = {"REGISTER", "UNDO"}

    path_enum: bpy.props.EnumProperty(
        items=[
            ("Assets", str(assets_p_file), ""),
            ("Addons", str(addons_p_file), ""),
        ]
    )  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        file_path = Path(self.path_enum)
        if not file_path.exists():
            self.report({"ERROR"}, f"预设文件 '{file_path.name}' 没有找到!")
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


CLASSES = [PIE_Open_Custom_XZ_presets_file_In_NewWindow]
class_register, class_unregister = bpy.utils.register_classes_factory(CLASSES)


def register():
    class_register()


def unregister():
    class_unregister()


if __name__ == "__main__":
    register()
