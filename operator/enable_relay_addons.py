import json
import string
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
# print(f"{third_ext_id=}")


def replace_substitute(op_args, placeholders):
    # 替换占位符
    for key, value in op_args.items():
        template = string.Template(value)
        if isinstance(value, str):
            op_args[key] = template.safe_substitute(placeholders)


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


def fix_no_userdefalt_folder():
    try:
        path = Path(bpy.utils.user_resource("EXTENSIONS")) / "user_default"
    except Exception as e:
        print(f"检索 User Default 路径时出错: {e}")
        path = None

    if path and not path.exists():
        try:
            path.mkdir(parents=True, exist_ok=True)
            print(f"已创建目录: {path}")
        except PermissionError as e:
            print(f"权限被拒绝: {e}")
        except OSError as e:
            print(f"创建目录时出错: {e}")


def convert_value2bool(value):
    if value in ["True", "False"]:
        return value == "True"
    else:
        return value


def install_addons(self, context):
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
                            print(f"已安装 - {addon_id} - 插件!")
                            bpy.ops.preferences.addon_enable(module=full_ext_id)
                        except:
                            self.report({"ERROR"}, "联网下载失败，请检查网络连接")
                    else:
                        # print(full_ext_id, "!!!", addon_utils.check(full_ext_id))
                        if not addon_utils.check(full_ext_id)[0]:
                            bpy.ops.preferences.addon_enable(module=full_ext_id)
                    set_ex_settings(context, full_ext_id, addon_sets)

            elif self.ex_dirs == "third_ex":
                if get_repos_class().get(third_repo_name) is None:
                    bpy.ops.preferences.extension_repo_add(remote_url=f"https://{third_repo_name}/xz", type="REMOTE")
                else:
                    enable_repos(third_repo_name)
                for addon_id, addon_sets in json_file_data[self.ex_dirs].items():
                    full_ext_id = f"{third_ext_id}.{addon_id}"
                    if full_ext_id not in get_addon_list():
                        repo_directory = repos.get(third_repo_name).directory
                        repo_index = repos.find(third_repo_name)
                        try:
                            bpy.ops.extensions.package_install(
                                "EXEC_DEFAULT",
                                repo_directory=repo_directory,
                                repo_index=repo_index,
                                pkg_id=addon_id,
                            )
                            self.report({"INFO"}, f"已安装 - {addon_id} - 插件!")
                        except:
                            self.report({"INFO"}, f"插件 {addon_id} 安装错误!")
                        # Register the timer function to wait for installation
                        try:
                            bpy.app.timers.register(wait_for_addon_install(context, full_ext_id, addon_sets))
                        except:
                            pass
                    print(bpy.app.timers.is_registered(wait_for_addon_install))
                    if bpy.app.timers.is_registered(wait_for_addon_install):
                        bpy.app.timers.unregister(wait_for_addon_install)
                    else:
                        if not addon_utils.check(full_ext_id)[0]:
                            try:
                                bpy.ops.preferences.addon_enable(module=full_ext_id)
                            except:
                                print(f"插件开启错误:{full_ext_id}")
                                pass
                        try:
                            set_ex_settings(context, full_ext_id, addon_sets)
                        except:
                            print(f"插件未开启，无法设置插件配置:{full_ext_id}")
                            pass

            else:
                return {"CANCELLED"}
        return {"FINISHED"}
    else:
        return {"CANCELLED"}


def wait_for_addon_install(context, full_ext_id, addon_sets):
    def _wait():
        if full_ext_id in get_addon_list():
            set_ex_settings(context, full_ext_id, addon_sets)
            return None  # 停止计时器
        else:
            return 0.2  # 再次重新检查，0.2秒

    return _wait


def set_ex_settings(context, full_ext_id, addon_sets):
    keymaps = get_keymaps_class()
    placeholders = {
        "CONFIG_PATH": get_config_path(),
        "SYNC_PATH": str(Path(get_prefs().assets_library_path_sync)),
        "LOCAL_PATH": str(Path(get_prefs().assets_library_path_local)),
        # 可以添加更多占位符
    }
    for sets_type, sets_data in addon_sets.items():
        if sets_type == "keymaps":
            set_interface_translate(False)
            for keymaps_items in sets_data:
                # 区分识别键列表和设置键列表
                key_identities = keymaps_items["identity"]
                key_key_set = keymaps_items["key_set"]
                identity_dict = {identity.split(":")[0]: identity.split(":")[1] for identity in key_identities}
                keysets_dict = {identity.split(":")[0]: identity.split(":")[1] for identity in key_key_set}
                converted_keysets_dict = {
                    k: (v == "True" if v in ["True", "False"] else v) for k, v in keysets_dict.items()
                }
                # print(f"{converted_keysets_dict=}")
                keymaps_name = identity_dict.pop("keymaps_name")
                keymap_items = keymaps.get(keymaps_name).keymap_items
                keymap_iter = [
                    keymap
                    for keymap in keymap_items
                    if all(
                        [
                            getattr(keymap, ident_name) == ident_value
                            for ident_name, ident_value in identity_dict.items()
                        ]
                    )
                ]
                if keymap_iter:
                    # print(f"{keymap_iter=}")
                    for key in keymap_iter:
                        for key_name, key_value in converted_keysets_dict.items():
                            try:
                                setattr(key, key_name, convert_value2bool(key_value))
                            except:
                                print(f"键位设置错误：{key}::{key_name}::{key_value}")
                else:
                    print(f"{full_ext_id}键位设置，未找到键名！已跳过设置")
            set_interface_translate(True)

        elif sets_type == "prefs":
            prefs = context.preferences.addons[full_ext_id].preferences
            replace_substitute(sets_data, placeholders)
            for prop_name, prop_value in sets_data.items():
                try:
                    setattr(prefs, prop_name, convert_value2bool(prop_value))
                except:
                    print(full_ext_id, "--插件属性设置错误-->", prop_name, ":", prop_value)

        elif sets_type == "runOP":
            for op_name, op_args in sets_data.items():
                replace_substitute(op_args, placeholders)

                op_class, op_func = op_name.split(".")
                try:
                    getattr(getattr(bpy.ops, op_class), op_func)(**op_args)
                except:
                    print("自动执行插件操作错误:\n", f"操作符:{op_name}\n", f"操作参数:{op_args}")


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
            text, icon = "配置作者常用插件预设,会较长卡住! 请耐心等待...", "ERROR"
        row = layout.row()

        row.label(text=text, icon=icon)

    def execute(self, context):
        if self.ex_dirs != "":
            install_addons(self, context)
            return {"FINISHED"}
        else:
            return {"CANCELLED"}


CLASSES = [Enable_Pie_Menu_Relay_Addons]


@persistent
def change_addons(dummy):
    if get_prefs().enable_addon_presets_items:
        bpy.ops.pie.enable_relay_addons(ex_dirs="sys_ex")
        bpy.ops.pie.enable_relay_addons(ex_dirs="org_ex")
        bpy.ops.pie.enable_relay_addons(ex_dirs="third_ex")
        print(f"{addon_name()} 已开启依赖插件")
        bpy.ops.wm.save_userpref()


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    # 修复找不到用户默认路径
    fix_no_userdefalt_folder()

    manage_app_handlers(handler_on_default_blender_list, change_addons)


def unregister():
    manage_app_handlers(handler_on_default_blender_list, change_addons, True)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
