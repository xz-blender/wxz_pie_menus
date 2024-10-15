import json
import os
import subprocess
import time
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

import bpy
from bpy.app.handlers import persistent

from ..items import *
from ..utils import *

nodes_dir_path = Path(__file__).parent.parent / "nodes_presets"

wxz_nodes_dir = nodes_dir_path / "wxz_nodes"
wxz_nodes_script = wxz_nodes_dir / "script.py"
save_time_file = wxz_nodes_dir / "blends_savetime.txt"


def set_wxz_nodes_presets():
    for root, dirs, files in os.walk(wxz_nodes_dir):
        for file in files:
            if file.endswith(".blend"):
                full_path = os.path.join(root, file)
                file_name = os.path.basename(file).split(".")[0]
                if save_time_file.exists():
                    with open(save_time_file, "r") as s_file:
                        name_save_time = file_name + "_SaveTime"
                        time_data = json.load(s_file)
                        time = time_data.get(name_save_time)
                        if time:
                            json_time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
                            timestamp = datetime.fromtimestamp(os.path.getmtime(full_path))

                            if abs((json_time - timestamp).total_seconds()) > 60:
                                subprocess.run(
                                    [
                                        bpy.app.binary_path,
                                        full_path,
                                        "--background",
                                        "--factory-startup",
                                        "--python",
                                        wxz_nodes_script,
                                    ]
                                )
                            else:
                                pass
                        else:
                            # print(f"{name_save_time} 文本内无保存时间!")
                            pass
                else:
                    # print(f"{save_time_file.name} 文件不存在!")
                    subprocess.run(
                        [
                            bpy.app.binary_path,
                            full_path,
                            "--background",
                            "--factory-startup",
                            "--python",
                            wxz_nodes_script,
                        ]
                    )


@persistent
def change_nodes_presets(dummy):
    if get_prefs().load_assets_library_presets:
        set_wxz_nodes_presets()
        print(f"{addon_name()} 已刷新wxz_nodes节点!")


def register():
    manage_app_handlers(handler_on_default_blender_list, change_nodes_presets)


def unregister():
    manage_app_handlers(handler_on_default_blender_list, change_nodes_presets, True)


if __name__ == "__main__":
    register()
