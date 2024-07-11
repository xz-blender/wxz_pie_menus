import os
import time
from pathlib import Path

import addon_utils
import bpy
from bpy.types import Operator

from ..utils import get_local_path, get_sync_path
from .extensions_setting import *

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


def get_addon_list():
    addon_utils.modules_refresh()
    addons_list = []
    for mod in addon_utils.modules():
        addons_list.append(mod.__name__)
    return addons_list


def change_addon_key_value(change_dir):
    bpy.context.preferences.view.use_translate_interface = False
    for dir_list in change_dir:
        keymaps = bpy.context.window_manager.keyconfigs["Blender addon"].keymaps
        for ks_name, ks_data in keymaps.items():
            if ks_name == dir_list[0][0]:
                list_keymaps = []
                for id_name, id_data in ks_data.keymap_items.items():
                    if id_name == dir_list[0][1] and id_data.name == dir_list[0][2]:
                        list_keymaps.append(id_data)
                for data in list_keymaps:
                    for value in dir_list[1]:
                        setattr(data, value[0], value[1])
                        # print(value[0], value[1])
                    if dir_list[2] != None:
                        for prop in dir_list[2]:
                            setattr(data.properties, prop[0], prop[1])
                list_keymaps.clear()
    bpy.context.preferences.view.use_translate_interface = True


def enable_addons(self, context, bl_ext_dict, remote_name=None):
    if bpy.app.version >= (4, 2, 0):
        if remote_name != None:
            context.preferences.extensions.repos[remote_name].enabled = True
            bpy.ops.extensions.repo_sync_all()
            bpy.ops.preferences.addon_refresh()
            prefix = "bl_ext." + remote_name.split(".", 1)[1].replace(".", "_") + "."
        else:
            prefix = ""
        for addon_name, addon_change in bl_ext_dict.items():
            addon_name = prefix + addon_name
            if addon_name in get_addon_list():
                if addon_utils.check(addon_name)[0] == False:
                    #  # check addon is enabled
                    try:
                        bpy.ops.preferences.addon_enable(module=addon_name)
                        print(addon_name, "插件已经打开")
                    except:
                        print(addon_name, "插件加载错误")
                if addon_change[0]:
                    for pref_change in addon_change[0]:
                        setattr(context.preferences.addons[addon_name].preferences, pref_change[0], pref_change[1])
                if addon_change[1]:
                    change_addon_key_value(addon_change[1])
            else:
                try:
                    bpy.ops.extensions.package_install(repo_index=0, pkg_id=addon_name)
                except:
                    print(addon_name, "插件下载失败")
        self.report({"INFO"}, "已开启预设插件")


class Enable_Pie_Menu_Relay_Addons(Operator):
    bl_idname = "pie.enable_relay_addons"
    bl_label = "一次性打开多个常用插件,会非常耗时!"
    bl_description = "一键打开常用内置插件"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
        # return self.execute(context)

    # def draw(self, context):
    #     layout = self.layout
    #     layout.label(text="一次性打开多个常用插件,会非常耗时!", icon="ERROR")

    def execute(self, context):
        try:
            enable_addons(self, context, blender_org_extensions, "extensions.blender.org")
            enable_addons(self, context, system_extensions)
        except:
            pass
        return {"FINISHED"}


def change_addons():
    bpy.context.preferences.filepaths.texture_directory = (
        str(Path(sync_path).parent.parent / "Texture") + os.sep
    ).replace("\\", "/")
    bpy.context.preferences.filepaths.font_directory = (str(Path(sync_path).parent.parent / "Fonts") + os.sep).replace(
        "\\", "/"
    )
    bpy.ops.pie.enable_relay_addons()
    print('"WXZ_Pie_Menu" Enable Relay Addons!')
    bpy.ops.wm.save_userpref()


def register():
    # try:
    bpy.utils.register_class(Enable_Pie_Menu_Relay_Addons)
    # except:
    #     pass
    if not bpy.app.timers.is_registered(change_addons):
        bpy.app.timers.register(change_addons, first_interval=2)


def unregister():
    if bpy.app.timers.is_registered(change_addons):
        bpy.app.timers.unregister(change_addons)

    bpy.utils.unregister_class(Enable_Pie_Menu_Relay_Addons)


if __name__ == "__main__":
    register()
