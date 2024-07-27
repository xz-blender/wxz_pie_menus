from pathlib import Path

import bpy

from .. import __package__ as base_package
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

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        sync_path = get_prefs().assets_library_path_sync
        local_path = get_prefs().assets_library_path_local

        setting_lib = {
            "Poly Haven": (str(Path(local_path) / "Poly Haven"), "LINK"),
            "旧公司资产": (str(Path(local_path) / "company_old_lib"), "APPEND_REUSE"),
            "Simple Cloth": (str(Path(sync_path) / "Simply Basic Cloth Library"), "APPEND"),
            "GN": (str(Path(sync_path) / "GN"), "APPEND_REUSE"),
            "GN_Assets": (str(Path(sync_path) / "GN_Assets"), "APPEND_REUSE"),
            "Material": (str(Path(sync_path) / "Material"), "APPEND_REUSE"),
            "Lights": (str(Path(sync_path) / "Lights"), "APPEND_REUSE"),
            "Abionic": (str(Path(local_path) / "Abionic"), "LINK"),
            "BagaPie Assets": (str(Path(local_path) / "BagaPie Assets"), "LINK"),
            "室内家具模型": (str(Path(local_path) / "室内家具模型"), "LINK"),
            "Geo-Scatter_library": (str(Path(local_path) / "Geo-Scatter_library"), "LINK"),
            "Trash_kit": (str(Path(local_path) / "Trash_kit"), "LINK"),
            "kit_bash": (str(Path(local_path) / "kit_bash"), "LINK"),
            "kit_building": (str(Path(local_path) / "kit_building"), "LINK"),
            "Tree Assets": (str(Path(local_path) / "Tree Assets"), "LINK"),
            "Motion Animate": (str(Path(local_path) / "Motion Animate"), "APPEND"),
            "图案光阴影贴图": (str(Path(local_path) / "图案光阴影贴图"), "LINK"),
            "其他": (str(Path(local_path) / "其他"), "LINK"),
            "GN_Tools": (str(Path(sync_path) / "GN_Tools"), "APPEND"),
            "BMS-东京后街": (str(Path(local_path) / "BMS-东京后街"), "LINK"),
            "RealCloud": (str(Path(local_path) / "RealCloud"), "LINK"),
            "DeepTree": (str(Path(local_path) / "DeepTree"), "LINK"),
            "光影灯光": (str(Path(local_path) / "Gobos Light Textures"), "LINK"),
        }
        app_lib_data = {}
        for lib in bpy.context.preferences.filepaths.asset_libraries:
            app_lib_data[lib.name] = lib.path
        change_assets_library_path(app_lib_data, setting_lib)

        # 设置默认 文件夹路径
        filepaths = context.preferences.filepaths
        parent_path = Path(sync_path).parent.parent
        filepaths.texture_directory = (str(parent_path / "Texture")).replace("\\", "/")
        filepaths.font_directory = (str(parent_path / "Fonts")).replace("\\", "/")

        return {"FINISHED"}


def change_assets_library_path(app_lib_data, setting_lib):
    # for name in app_lib_data:
    #     df_name = 'User Library'
    #     if name == df_name:
    #         bpy.ops.preferences.asset_library_remove(index = app_lib_data.index(df_name))

    sort_setting_lib = dict(sorted(setting_lib.items(), key=lambda x: x[0]))

    for name, data in sort_setting_lib.items():
        asset_libraries = bpy.context.preferences.filepaths.asset_libraries
        if name not in app_lib_data:
            bpy.ops.preferences.asset_library_add(directory=data[0])
            asset_libraries[-1].name = name

            if bpy.app.version >= (3, 5, 0):
                asset_libraries[-1].import_method = data[1]

        else:
            asset_libraries.get(name).path = data[0]

    print('"WXZ_Pie_Menu"Changed Assets library')


def run_set_assets_library_path(dummy):
    if get_prefs().load_assets_library_presets:
        bpy.ops.pie.change_assets_library_path()


def register():
    bpy.utils.register_class(PIE_Change_Assets_library_Path)
    bpy.app.handlers.load_post.append(run_set_assets_library_path)


def unregister():
    bpy.utils.unregister_class(PIE_Change_Assets_library_Path)
    bpy.app.handlers.load_post.remove(run_set_assets_library_path)


# def register():
#     if not bpy.app.timers.is_registered(change_assets_library_path):
#         bpy.app.timers.register(change_assets_library_path, first_interval=2)


# def unregister():
#     if bpy.app.timers.is_registered(change_assets_library_path):
#         bpy.app.timers.unregister(change_assets_library_path)


if __name__ == "__main__":
    register()
