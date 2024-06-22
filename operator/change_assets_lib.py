from pathlib import Path

import bpy

from ..utils import get_local_path, get_sync_path

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (4, 1, 0),
    "location": "View3D",
    "category": "3D View",
}

sync_path = get_sync_path()
local_path = get_local_path()

setting_lib = {
    "Rig_Car": (str(Path(local_path) / "rig_cars"), "LINK"),
    "Poly Haven": (str(Path(local_path) / "Poly Haven"), "LINK"),
    "旧公司资产": (str(Path(local_path) / "company_old_lib"), "APPEND_REUSE"),
    "Simple Cloth": (str(Path(sync_path) / "Blender Assets Browser" / "Simply Basic Cloth Library"), "APPEND"),
    "GN": (str(Path(sync_path) / "Blender Assets Browser" / "GN"), "APPEND_REUSE"),
    "GN_Assets": (str(Path(sync_path) / "Blender Assets Browser" / "GN_Assets"), "APPEND_REUSE"),
    "Material": (str(Path(sync_path) / "Blender Assets Browser" / "Material"), "APPEND_REUSE"),
    "Lights": (str(Path(sync_path) / "Blender Assets Browser" / "Lights"), "APPEND_REUSE"),
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
    "GN_Tools": (str(Path(sync_path) / "Blender Assets Browser" / "GN_Tools"), "APPEND"),
    "BMS-东京后街": (str(Path(local_path) / "BMS-东京后街"), "LINK"),
    "RealCloud": (str(Path(local_path) / "RealCloud"), "LINK"),
    "DeepTree": (str(Path(local_path) / "DeepTree"), "LINK"),
}
app_lib_data = {}
for lib in bpy.context.preferences.filepaths.asset_libraries:
    app_lib_data[lib.name] = lib.path


def change_assets_library_path():
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

            version = bpy.app.version
            if version[0] >= 3 and version[1] >= 5:
                asset_libraries[-1].import_method = data[1]
        else:
            asset_libraries[name].path = data[0]

    print('"WXZ_Pie_Menu"Changed Assets library')


def register():
    if not bpy.app.timers.is_registered(change_assets_library_path):
        bpy.app.timers.register(change_assets_library_path, first_interval=2)


def unregister():
    if bpy.app.timers.is_registered(change_assets_library_path):
        bpy.app.timers.unregister(change_assets_library_path)


if __name__ == "__main__":
    register()
