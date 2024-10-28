import json
from collections import OrderedDict
from pathlib import Path

import bpy
from bpy.app.handlers import persistent

from ..items import *
from ..utils import *


class PIE_Change_Assets_library_Path(bpy.types.Operator):
    bl_idname = "pie.change_assets_library_path"
    bl_label = "添加xz的资产库预设"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    remove: bpy.props.BoolProperty(default=False)  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        sync = Path(get_prefs().assets_library_path_sync)
        local = Path(get_prefs().assets_library_path_local)
        nodes_dir_path = Path(__file__).parent.parent / "nodes_presets"
        presets_json_file = Path(__file__).parent / "assets_lib_presets.json"

        custom_assets_lib = {}
        with open(presets_json_file, "r") as json_file:
            data = json.load(json_file)

            divisors = {"sync": sync, "local": local}
            for key, divisor in divisors.items():
                for sub_key, sub_value in data[key].items():
                    path = sub_value[0] / divisor
                    if path.exists():
                        sub_value[0] = path.resolve()
                    else:
                        data[key].pop(sub_key)
                        print(f"找不到资源库路径 {sub_key} ! 请检查路径!")

            custom_assets_lib = {**data["sync"], **data["local"]}

        # 添加自定义的节点文件夹到字典中
        for item in nodes_dir_path.iterdir():
            if item.is_dir():
                custom_assets_lib[item.name] = str(item)

        if not self.remove:
            change_assets_library_path(custom_assets_lib)
            print(f"{addon_name()} -已添加- 资产库路径预设!")

        else:
            change_assets_library_path(custom_assets_lib, True)
            self.remove = False
            print(f"{addon_name()} -已移除- 资产库路径预设!")

        # 设置默认 文件夹路径
        filepaths = context.preferences.filepaths
        parent_path = sync.parent
        filepaths.texture_directory = str(parent_path / "Texture")
        filepaths.font_directory = str(parent_path / "Fonts")

        return {"FINISHED"}


def change_assets_library_path(custom_assets_lib, remove=False):
    as_lib = bpy.context.preferences.filepaths.asset_libraries
    custom_assets_lib = OrderedDict(sorted(custom_assets_lib.items()))
    import_method_dir = ["APPEND_REUSE", "APPEND", "LINK"]
    if not remove:
        for name, data in custom_assets_lib.items():
            if name not in as_lib:
                if isinstance(data, list):
                    path, method = data[0], data[1]
                    new_item = as_lib.new(name=name, directory=str(path))
                    new_item.import_method = import_method_dir[method]
                else:
                    new_item = as_lib.new(name=name, directory=str(data))

    else:
        for name in custom_assets_lib.keys():
            if name in as_lib:
                as_lib.remove(as_lib.get(name))


@persistent
def run_set_assets_library_path(dummy):
    if get_prefs().load_assets_library_presets:
        bpy.ops.pie.change_assets_library_path()


CLASSES = [
    PIE_Change_Assets_library_Path,
]


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    manage_app_handlers(handler_on_default_blender_list, run_set_assets_library_path)


def unregister():
    manage_app_handlers(handler_on_default_blender_list, run_set_assets_library_path, True)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
