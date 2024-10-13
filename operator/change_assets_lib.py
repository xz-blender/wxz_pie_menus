from collections import OrderedDict
from pathlib import Path

import bpy
from bpy.app.handlers import persistent

from ..items import *
from ..utils import *

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (4, 1, 0),
    "location": "View3D",
    "category": "3D View",
}


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

        custom_assets_lib = {
            "Poly Haven": (local / "Poly Haven", "LINK"),
            "旧公司资产": (local / "company_old_lib", "APPEND_REUSE"),
            "Simple Cloth": (sync / "Simply Basic Cloth Library", "APPEND"),
            "GN": (sync / "GN", "APPEND_REUSE"),
            "GN_Assets": (sync / "GN_Assets", "APPEND_REUSE"),
            "Material": (sync / "Material", "APPEND_REUSE"),
            "Lights": (sync / "Lights", "APPEND_REUSE"),
            "Abionic": (local / "Abionic", "LINK"),
            "BagaPie Assets": (local / "BagaPie Assets", "LINK"),
            "室内家具模型": (local / "室内家具模型", "LINK"),
            "Geo-Scatter_library": (local / "Geo-Scatter_library", "LINK"),
            "Trash_kit": (local / "Trash_kit", "LINK"),
            "Tree Assets": (local / "Tree Assets", "LINK"),
            "Motion Animate": (local / "Motion Animate", "APPEND"),
            "GN_Tools": (sync / "GN_Tools", "APPEND"),
            "RealCloud": (local / "RealCloud", "LINK"),
            "DeepTree": (local / "DeepTree", "LINK"),
            "光影灯光": (local / "Gobos Light Textures", "LINK"),
        }
        for item in nodes_dir_path.iterdir():
            if item.is_dir():
                custom_assets_lib[item.name] = str(item)

        if not self.remove:
            change_assets_library_path(custom_assets_lib)
            print(f"{addon_name()} -已添加- 资产库路径预设!")

        else:
            change_assets_library_path(custom_assets_lib, True)
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
    if not remove:
        for name, data in custom_assets_lib.items():
            if name not in as_lib:
                if isinstance(data, tuple):
                    path, method = data
                    new_item = as_lib.new(name=name, directory=str(path))
                    new_item.import_method = method
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


def register():
    bpy.utils.register_class(PIE_Change_Assets_library_Path)
    manage_app_handlers(handler_on_default_blender_list, run_set_assets_library_path)


def unregister():
    manage_app_handlers(handler_on_default_blender_list, run_set_assets_library_path, True)
    bpy.utils.unregister_class(PIE_Change_Assets_library_Path)


if __name__ == "__main__":
    register()
