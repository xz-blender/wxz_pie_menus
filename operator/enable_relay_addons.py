import json
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

ex_presets_file = Path(__file__).parent / "addons_lib_presets.json"
org_repo_name = "extensions.blender.org"
third_repo_name = "blender4.com"

repos = bpy.context.preferences.extensions.repos


def get_repo_module_name(repo_name):
    return repos[repo_name].module


org_ext_id = f"bl_ext.{get_repo_module_name(org_repo_name)}"
third_ext_id = f"bl_ext.{get_repo_module_name(third_repo_name)}"

org_dirPath = Path(repos.get(org_repo_name).directory)
third_dirPath = Path(repos.get(third_repo_name).directory)


def get_addon_list() -> tuple:
    addon_utils.modules_refresh()
    addons_list = []
    for mod in addon_utils.modules():
        addons_list.append(mod.__name__)
        # if get_prefs().debug:
        #     print(mod.__name__, "!!!!!!")
    return addons_list


def get_repos_class():
    return bpy.context.preferences.extensions.repos


def enable_repos(remote_name):
    get_repos_class().get(remote_name).enabled = True


def get_keymaps_class():
    return bpy.context.window_manager.keyconfigs.addon.keymaps


def set_interface_translate(bool):
    bpy.context.preferences.view.use_translate_interface = bool


def set_online():
    if not bpy.context.preferences.system.use_online_access:
        bpy.ops.extensions.userpref_allow_online()


def is_BlenderVersion_gthan(version: tuple = (4, 2, 0)):
    return bpy.app.version >= version


def install_addons_subfunction(self, json_file_data):
    for addon_id, addon_sets in json_file_data[self.ex_dirs].items():
        full_ext_id = f"{org_ext_id}.{addon_id}"
        if full_ext_id not in get_addon_list():
            try:
                download_zip(f"{org_repo_name}/{addon_id}.zip", org_dirPath)
                addon_utils.modules_refresh()
                addon_utils.enable(addon_id, default_set=True)
            except:
                self.report({"ERROR"}, "联网下载失败，请检查网络连接")
                return {"CANCELLED"}
        else:
            if addon_utils.check(full_ext_id)[0]:
                addon_utils.enable(full_ext_id)
        set_ex_settings(addon_sets)


def install_addons(self):
    set_online()
    if is_BlenderVersion_gthan():
        with ex_presets_file.open(encoding="utf-8") as json_file:
            json_file_data = json.load(json_file)
            if self.ex_dirs == "sys_ex":
                enable_repos("System")
                for addon_id, addon_sets in json_file_data[self.ex_dirs].items():
                    addon_utils.enable(addon_id, default_set=True)

            elif self.ex_dirs == "org_ex":
                enable_repos(org_repo_name)
                for addon_id, addon_sets in json_file_data[self.ex_dirs].items():
                    full_ext_id = f"{org_ext_id}.{addon_id}"
                    if full_ext_id not in get_addon_list():
                        try:
                            download_zip(f"{org_repo_name}/{addon_id}.zip", org_dirPath)
                            addon_utils.modules_refresh()
                            bpy.ops.preferences.addon_enable(module=full_ext_id)
                        except:
                            self.report({"ERROR"}, "联网下载失败，请检查网络连接")
                    else:
                        if addon_utils.check(full_ext_id)[0]:
                            bpy.ops.preferences.addon_enable(module=full_ext_id)
                    set_ex_settings(addon_sets)

            elif self.ex_dirs == "third_ex":
                if get_repos_class().get(third_repo_name) is None:
                    bpy.ops.preferences.extension_repo_add(remote_url=f"https://{third_repo_name}/xz", type="REMOTE")
                else:
                    enable_repos(third_repo_name)
                for addon_id, addon_sets in json_file_data[self.ex_dirs].items():
                    full_ext_id = f"{org_ext_id}.{addon_id}"
                    if full_ext_id not in get_addon_list():
                        repo_directory = repos.get(third_repo_name).directory
                        repo_index = repos.find(third_repo_name)
                        try:
                            bpy.ops.extensions.package_install(
                                "INVOKE_DEFAULT",
                                repo_directory=repo_directory,
                                repo_index=repo_index,
                                pkg_id=addon_id,
                            )
                            self.report({"INFO"}, f"已安装 - {addon_id} - 插件!")
                        except:
                            self.report({"INFO"}, f"插件 {addon_id} 安装错误!")
                    else:
                        if addon_utils.check(full_ext_id)[0]:
                            bpy.ops.preferences.addon_enable(module=full_ext_id)
                    set_ex_settings(addon_sets)
            else:
                return {"CANCELLED"}
        return {"FINISHED"}
    else:
        return {"CANCELLED"}


def set_ex_settings(change_dic):
    set_interface_translate(False)
    keymaps = get_keymaps_class()
    for sets_type, sets_data in change_dic:
        if sets_type == "keymaps":
            for sets in sets_data:
                keymap_items = keymaps.get(sets["space_name"]).keymap_items
                for keys_id, keys_data in keymap_items.items():
                    if sets.get("keymap_props") is None:
                        if all(keys_id == sets["keymap_id"], keys_data.name == sets["keymap_name"]):
                            setattr(keys_data, sets["keymap_prop"], sets["keymap_value"])
                    else:
                        pass
        elif sets_type == "prefs":
            ...


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
        if remote_name == "":
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
    bl_label = "一键安装或打开插件!"
    bl_description = ""
    bl_options = {"REGISTER"}

    ex_dirs: bpy.props.StringProperty()  # type: ignore

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        if self.ex_dirs == "sys_ex":
            return self.execute(context)
        else:
            return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        if self.ex_dirs == "sys_ex":
            text, icon = "一键开启内置插件", "INFO"
        elif self.ex_dirs == "org_ex":
            text, icon = "下载常用官方插件,大小2MB", "INFO"
        elif self.ex_dirs == "third_ex":
            text, icon = "下载作者常用插件,会短暂卡住! 请耐心等待...", "ERROR"
        row = layout.row()

        row.label(text=text, icon=icon)

    def execute(self, context):
        # try:
        #     enable_addons(self, context, blender_org_extensions, "extensions.blender.org")
        #     enable_addons(self, context, None, "blender4.com")
        #     enable_addons(self, context, system_extensions)
        # except:
        #     pass
        install_addons(self)
        return {"FINISHED"}


CLASSES = [Enable_Pie_Menu_Relay_Addons]


@persistent
def change_addons(dummy):
    if get_prefs().enable_addon_presets_items:
        bpy.ops.pie.enable_relay_addons()
        print(f"{addon_name()} 已开启依赖插件")
        bpy.ops.wm.save_userpref()


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    # get_addon_list()

    manage_app_handlers(handler_on_default_blender_list, change_addons)


def unregister():
    manage_app_handlers(handler_on_default_blender_list, change_addons, True)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
