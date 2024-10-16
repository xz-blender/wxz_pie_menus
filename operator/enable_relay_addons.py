import os
import time
from pathlib import Path

import addon_utils
import bpy
from bpy.app.handlers import persistent
from bpy.types import Operator

from ..download import download_zip
from ..items import *
from ..utils import *
from .extensions_setting import *


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
                    if dir_list[2] != None:
                        for prop in dir_list[2]:
                            setattr(data.properties, prop[0], prop[1])
                list_keymaps.clear()
    bpy.context.preferences.view.use_translate_interface = True


def enable_addons(self, context, bl_ext_dict, remote_name=None):
    if bpy.app.version >= (4, 2, 0):
        if remote_name == "extensions.blender.org":
            rep_directory = context.preferences.extensions.repos[remote_name].directory + "/"
            # print("-----------", rep_directory)
            # print(xz_url)
            for addon_name in blender_org_extensions.keys():
                if get_prefs().download_official_addons:
                    try:
                        download_zip(remote_name + "/" + f"{addon_name}.zip", rep_directory)
                    except:
                        print("----", addon_name, " 插件下载失败")
        # bpy.ops.extensions.package_install

        # 检查 rep_directory 下的 xz_ex_check.txt 文件内的存储版本号，如果不匹配则重新下载
        # if Path(rep_directory + "xz_ex_check.txt").exists():
        #     with open(rep_directory + "xz_ex_check.txt", "r") as f:
        #         local_version = f.read()
        #     if local_version != blender_org_extensions["xz_ex_check"]:
        #         print("----", "插件版本号不匹配，正在重新下载")
        #         for addon_name in blender_org_extensions.keys():
        #             try:
        #                 download_zip(remote_name + "/" + f"{addon_name}.zip", rep_directory)
        #             except:
        #                 print("----", addon_name, " 插件下载失败")

        repos_keys = context.preferences.extensions.repos.keys()
        if remote_name not in repos_keys:
            bpy.ops.preferences.extension_repo_add(remote_url="https://" + remote_name + "/xz", type="REMOTE")
        elif remote_name in repos_keys:
            context.preferences.extensions.repos[remote_name].enabled = True
            # bpy.ops.extensions.repo_sync_all()
            bpy.ops.preferences.addon_refresh()
            prefix = "bl_ext." + remote_name.split(".", 1)[1].replace(".", "_") + "."
        else:
            prefix = ""

        if bl_ext_dict:
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

            self.report({"INFO"}, "已开启预设插件")


class Enable_Pie_Menu_Relay_Addons(Operator):
    bl_idname = "pie.enable_relay_addons"
    bl_label = "一键安装多个插件!"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="下载时,网速过慢可能会短暂卡住!  请耐心等待...", icon="ERROR")

    def execute(self, context):
        try:
            enable_addons(self, context, blender_org_extensions, "extensions.blender.org")
            enable_addons(self, context, None, "blender4.com")
            enable_addons(self, context, system_extensions)
        except:
            pass
        return {"FINISHED"}


CLASSES = [Enable_Pie_Menu_Relay_Addons]
class_register, class_unrigister = bpy.utils.register_classes_factory(CLASSES)


@persistent
def change_addons():
    if get_prefs().enable_addon_presets_items:
        bpy.ops.pie.enable_relay_addons()
        print(f"{addon_name()} 已开启依赖插件")
        bpy.ops.wm.save_userpref()


def register():
    class_register()
    manage_app_handlers(handler_on_default_blender_list, change_addons)


def unregister():
    manage_app_handlers(handler_on_default_blender_list, change_addons, True)
    class_unrigister()


if __name__ == "__main__":
    register()
