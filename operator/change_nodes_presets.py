import json
import os
import subprocess
from pathlib import Path

import bpy

submoduname = __name__.split(".")[-1]
bl_info = {
    "name": submoduname,
    "author": "wxz",
    "version": (0, 0, 1),
    "blender": (4, 1, 0),
    "location": "View3D",
    "category": "3D View",
}


nodes_dir_path = Path(__file__).parent.parent / "nodes_presets"
nodes_dir_path_list = {}

for item in nodes_dir_path.iterdir():
    if item.is_dir():
        nodes_dir_path_list[item.name] = str(item)


app_lib_data = {}
for lib in bpy.context.preferences.filepaths.asset_libraries:
    app_lib_data[lib.name] = lib.path


def change_assets_library_path():
    sort_nodes_path_list = dict(sorted(nodes_dir_path_list.items(), key=lambda x: x))
    for name, path in sort_nodes_path_list.items():
        asset_libraries = bpy.context.preferences.filepaths.asset_libraries
        if name not in app_lib_data:
            bpy.ops.preferences.asset_library_add(directory=path)
            asset_libraries[-1].name = name
        else:
            asset_libraries.get(name).path = path

    nodes_dir_path_list.clear()
    app_lib_data.clear()


wxz_nodes_dir = nodes_dir_path / "wxz_nodes"
wxz_nodes_script = wxz_nodes_dir / "script.py"


def set_wxz_nodes_presets():
    for root, dirs, files in os.walk(wxz_nodes_dir):
        for file in files:
            if file.endswith(".blend"):
                full_path = os.path.join(root, file)
                subprocess.run([bpy.app.binary_path, full_path, "--background", "--python", wxz_nodes_script])


def change_nodes_presets():
    change_assets_library_path()
    set_wxz_nodes_presets()
    print('"WXZ_Pie_Menu" Add Default Nodes Presets')


def register():
    if not bpy.app.timers.is_registered(change_nodes_presets):
        bpy.app.timers.register(change_nodes_presets, first_interval=1)


def unregister():
    if bpy.app.timers.is_registered(change_nodes_presets):
        bpy.app.timers.unregister(change_nodes_presets)


if __name__ == "__main__":
    register()
