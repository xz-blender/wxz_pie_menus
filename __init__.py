from pathlib import Path

from .download import download_file, download_zip
from .packup import split_file_list, split_folder_list

down_path = Path(__file__).parent
xz_url = "addons_file/" + str(down_path.name) + "/"
for file in split_file_list:
    download_file(xz_url + file, down_path)
for dir in split_folder_list:
    download_zip(xz_url + dir + ".zip", down_path)

import site
import subprocess
import sys

import bpy
from bpy.props import *
from bpy.types import AddonPreferences, Operator, PropertyGroup, UIList

from . import props
from .nodes_presets.Higssas import *
from .translation.translate import GetTranslationDict
from .utils import *

bl_info = {
    "name": "WXZ Pie Menus Addon",
    "author": "wxz",
    "version": (0, 1, 10),
    "blender": (4, 2, 0),
    "description": "Pie Menu",
    "category": "3D View",
}

except_module_list = [
    "icons",
    "__pycache__",
    ".DS_Store",
    "utils",
    "Brush-key",
    "operator_id",
    "operator_id_sort",
    "extensions_setting",
]
cwd = Path(__file__).parent
module_path_name_list = {"pie": "pie_modules", "parts_addons": "other_modules", "operator": "setting_modules"}
all_modules = []
all_modules_dir = {}
for module_path, module_name in module_path_name_list.items():
    iter_module = iter_submodules_name(Path(cwd) / module_path, except_module_list)
    all_modules += iter_module
    all_modules_dir[module_name] = iter_module


app_path = site.getusersitepackages()
# print("Blender PIP user site:", app_path)
if app_path not in sys.path:
    # print("Adding site to path")
    sys.path.append(app_path)

MODULES_FOLDER = Path(bpy.utils.system_resource("SCRIPTS")) / "modules"
python_bin = sys.executable
TEXT_OUTPUT = []
ERROR_OUTPUT = []
addon_keymaps = []


def run_pip_command(self, *cmds, cols=False, run_module="pip"):
    """使用user spec命令运行P IP进程"""
    global ERROR_OUTPUT
    global TEXT_OUTPUT

    cmds = [c for c in cmds if c is not None]
    command = [python_bin, "-m", run_module, *cmds]
    if get_prefs().pip_use_china_sources:
        command += ["-i", "https://pypi.tuna.tsinghua.edu.cn/simple"]
    print("RUN_CMD:", command)
    output = subprocess.run(command, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if output.stderr:
        if "WARNING" not in output.stderr[:20]:
            # Don't display error popup when PIP complains it's not the latest and greatest
            self.report({"ERROR"}, "发生错误. 请检查控制台详细信息")
        print(">>>------------ ERROR ------------")
        print(">>> Rturn Code :", output.returncode)
        print(">>> STD Error :", output.stderr)
        ERROR_OUTPUT = save_text(output.stderr)
    else:
        ERROR_OUTPUT = []

    if output.stdout:
        TEXT_OUTPUT = save_text(output.stdout, cols=cols)
    else:
        TEXT_OUTPUT = []


def save_text(text, cols=False):
    """将输入文本字符串转换为2列的列表"""
    out = []
    for i in text.split("\n"):
        if len(i) <= 1:
            continue
        subs = i.split()
        parts = []
        if cols:
            for s in subs:
                parts.append(s)
        else:
            parts.append(" ".join(subs))
        out.append(parts)
    return out


class PIE_OT_PIPInstall(Operator):
    bl_idname = "pie.pip_install"
    bl_label = "安装"
    bl_description = "安装PIP包"

    def execute(self, context):
        chosen_path = "--user" if get_prefs().pip_user_flag else None
        run_pip_command(
            self,
            "install",
            *get_prefs().pip_module_name.split(" "),
            chosen_path,
        )
        return {"FINISHED"}


class PIE_OT_PIPInstall_Default(Operator):
    bl_idname = "pie.pip_install_default"
    bl_label = "安装本插件需要的包"
    bl_description = "安装本插件需要的PIP默认包"

    def execute(self, context):
        chosen_path = "--user" if get_prefs().pip_user_flag else None
        pkg = [p.name for p in get_prefs().bl_rna.properties["default_pkg"].enum_items]
        run_pip_command(
            self,
            "install",
            *pkg,
            chosen_path,
        )
        self.report({"INFO"}, "默认包已安装,需要重启Blender！")
        return {"FINISHED"}


class PIE_OT_PIPRemove(Operator):
    bl_idname = "pie.pip_remove"
    bl_label = "卸载(需重启)"
    bl_description = "移除PIP包"

    def execute(self, context):
        save_prop = get_prefs().pip_use_china_sources
        setattr(get_prefs(), "pip_use_china_sources", False)
        run_pip_command(self, "uninstall", *get_prefs().pip_module_name.split(" "), "-y")
        setattr(get_prefs(), "pip_use_china_sources", save_prop)
        return {"FINISHED"}


class PIE_OT_ClearText(Operator):
    bl_idname = "pie.pip_cleartext"
    bl_label = "清除文本"
    bl_description = "清除输出的文本"

    def execute(self, context):
        global TEXT_OUTPUT
        TEXT_OUTPUT = []
        global ERROR_OUTPUT
        ERROR_OUTPUT = []
        return {"FINISHED"}


class PIE_OT_PIPList(Operator):
    bl_idname = "pie.pip_show_list"
    bl_label = "列出已安装包"
    bl_description = "列出已安装的PIP软件包"

    def execute(self, context):
        run_pip_command(self, "list", cols=True)
        return {"FINISHED"}


class PIE_OT_EnsurePIP(Operator):
    bl_idname = "pie.ensure_pip"
    bl_label = "验证PIP程序"
    bl_description = "尝试确保PIP安装程序存在"

    def execute(self, context):
        run_pip_command(self, "--default-pip", run_module="ensurepip")
        return {"FINISHED"}


class PIE_OT_UpgradePIP(Operator):
    bl_idname = "pie.upgrade_pip"
    bl_label = "升级PIP"
    bl_description = "升级PIP"

    def execute(self, context):
        run_pip_command(self, "install", "--upgrade", "pip")
        return {"FINISHED"}


def _get_pref_class(mod):
    import inspect

    for obj in vars(mod).values():
        if inspect.isclass(obj) and issubclass(obj, PropertyGroup):
            if hasattr(obj, "bl_idname") and obj.bl_idname == mod.__name__:
                return obj


def get_addon_preferences(name=""):
    """Acquisition and registration"""
    addons = bpy.context.preferences.addons
    if __name__ not in addons:  # wm.read_factory_settings()
        return None
    addon_prefs = addons[__name__].preferences
    if name:
        if not hasattr(addon_prefs, name):
            for mod in all_modules:
                if mod.__name__.split(".")[-1] == name:
                    cls = _get_pref_class(mod)
                    if cls:
                        prop = PointerProperty(type=cls)
                        create_property(WXZ_PIE_Preferences, name, prop)
                        bpy.utils.unregister_class(WXZ_PIE_Preferences)
                        bpy.utils.register_class(WXZ_PIE_Preferences)
        return getattr(addon_prefs, name, None)
    else:
        return addon_prefs


def create_property(cls, name, prop):
    if not hasattr(cls, "__annotations__"):
        cls.__annotations__ = dict()
    cls.__annotations__[name] = prop


def register_submodule(mod):
    try:
        mod.register()
    except ValueError as error:
        print(error)
        pass
    try:
        # if hasattr(mod.bl_info):
        mod.__addon_enabled__ = True
    except:
        pass


def unregister_submodule(mod):
    if mod.__addon_enabled__:
        mod.unregister()
        mod.__addon_enabled__ = False

        prefs = get_addon_preferences()
        name = mod.__name__.split(".")[-1]
        if hasattr(WXZ_PIE_Preferences, name):
            delattr(WXZ_PIE_Preferences, name)
            if prefs:
                bpy.utils.unregister_class(WXZ_PIE_Preferences)
                bpy.utils.register_class(WXZ_PIE_Preferences)
                if name in prefs:
                    del prefs[name]


class PIE_UL_pie_modules(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        mod_name = item.name
        row = layout.row()
        row.label(text=mod_name)
        row.prop(data, "use_" + mod_name, text="")


class PIE_UL_other_modules(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        mod_name = item.name
        row = layout.row()
        row.label(text=mod_name)
        row.prop(data, "use_" + mod_name, text="")


class PIE_UL_setting_modules(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        mod_name = item.name
        row = layout.row()
        row.label(text=mod_name)
        row.prop(data, "use_" + mod_name, text="")


def draw_pie_modules(self, top_row, module_path_name_list):
    for lable_name, module_name in {
        "已启用饼菜单:": "pie",
        "已启用内置插件:": "parts_addons",
        "已应用设置:": "operator",
    }.items():
        split = top_row.split()
        box = split.box()
        sub_row = box.row()
        sub_row.alignment = "CENTER"
        sub_row.label(text=lable_name)
        sub_row = box.row()
        column = sub_row.column()

        name = module_path_name_list[module_name].split("_")[0]
        # print(module_name, "__________", name)
        column.template_list(
            f"PIE_UL_{name}_modules", "", self, f"{name}_modules", self, f"{name}_modules_index", rows=8
        )


class WXZ_PIE_Preferences(AddonPreferences, props.WXZ_PIE_Prefs_Props):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "tabs", expand=True)
        row.alignment = "CENTER"

        box = layout.box()
        if self.tabs == "DEPENDENCIES":
            self.draw_dependencies(box)
        elif self.tabs == "ADDON_MENUS":
            self.draw_addon_menus(box, context)
        elif self.tabs == "RESOURCE_CONFIG":
            self.draw_resource_config(box)
        elif self.tabs == "Other_Addons_Setting":
            self.draw_other_addons_setting(box)

    def draw_dependencies(self, layout):
        layout.label(text="依赖包设置")
        layout = self.layout
        row = layout.row()
        row.prop(self, "pip_user_flag", text="使用Blender的Python目录")
        row.prop(self, "pip_use_china_sources", text="使用清华镜像源进行下载")

        row = layout.row()
        split = row.split(factor=0.65)
        row_l = split.row()
        row_l.operator("pie.ensure_pip")
        row_r = split.row(align=True)
        row_r.operator("pie.upgrade_pip")
        row_r.operator("pie.pip_show_list")

        row = layout.row(align=True)
        split = row.split(factor=0.65)
        split.scale_y = 1.4
        row_l = split.row()
        split_l = row_l.split(factor=0.4, align=True)
        row_ll = split_l.row()
        row_ll.label(text="输入包名(空格分割):")
        row_lr = split_l.row()
        row_lr.prop(self, "pip_module_name", text="")
        row_r = split.row(align=True)
        row_r.operator("pie.pip_install")
        row_r.operator("pie.pip_remove")

        row = layout.row()
        split = row.split(factor=0.65)
        split_l = split.row(align=True)
        for item in self.bl_rna.properties["default_pkg"].enum_items:
            box = split_l.box()
            try:
                __import__(item.description)
                icon = "CHECKMARK"
            except ImportError:
                icon = "PANEL_CLOSE"
            box.label(text=item.name, icon=icon)
        split_r = split.row()
        split_r.scale_y = 1.4
        split_r.operator("pie.pip_install_default")

        if TEXT_OUTPUT != []:
            row = layout.row(align=True)
            box = row.box()
            box = box.column(align=True)
            for i in TEXT_OUTPUT:
                row = box.row()
                for s in i:
                    col = row.column()
                    col.label(text=s)
            row = layout.row()

        if ERROR_OUTPUT != []:
            row = layout.row(align=True)
            box = row.box()
            box = box.column(align=True)
            for i in ERROR_OUTPUT:
                row = box.row()
                for s in i:
                    col = row.column()
                    col.label(text=s)
            row = layout.row()

        if TEXT_OUTPUT != [] or ERROR_OUTPUT != []:
            row.operator("pie.pip_cleartext", text="清除文本")

    def draw_addon_menus(self, layout, context):
        layout.label(text="内置饼菜单 & 内置插件开关")
        top_row = layout.row()
        draw_pie_modules(self, top_row, module_path_name_list)

    def draw_resource_config(self, layout):
        layout.label(text="以下选项会严重更改您的软件设置,谨慎选择 (重启自动运行 & 勾选并手动运行)", icon="ERROR")
        box = layout.box()
        row = box.row()
        row.alignment = "LEFT"

        row = box.row()
        text_download_addons = "加载插件 - 常用外部插件预设 (自动下载)"
        if self.download_official_addons:
            split = row.column().split(factor=0.8)
            split.alignment = "LEFT"
            split.prop(self, "download_official_addons", text=text_download_addons)
            split.alignment = "RIGHT"
            split.operator("pie.enable_relay_addons", text="手动执行")
        else:
            row.alignment = "LEFT"
            row.prop(self, "download_official_addons", text=text_download_addons)

        row = box.row()
        if not self.load_assets_library_presets:
            row.prop(self, "load_assets_library_presets", text="加载预设 - 资源库路径 (会增加许多对您无用的资产路径!)")
        else:
            sp = row.split(factor=0.8)
            sp.prop(self, "load_assets_library_presets", text="加载预设 - 资源库路径 (会增加许多对您无用的资产路径!)")
            sp.operator("pie.change_assets_library_path", text="移除路径").remove = True

            split = box.split(factor=0.8)
            box_l = split.box()
            row = box_l.row()
            row.prop(self, "assets_library_path_sync")
            row = box_l.row()
            row.prop(self, "assets_library_path_local")
            box_r = split.box()
            row = box_r.row()
            row.scale_y = 2.4
            row.operator("pie.change_assets_library_path", text="手动执行")

        row = box.row()
        text_hotkey = "加载预设 - 快捷键 (请备份好您的快捷键!)"
        if self.load_xz_keys_presets:
            split = row.column().split(factor=0.8)
            split.alignment = "LEFT"
            split.prop(self, "load_xz_keys_presets", text=text_hotkey)
            split.alignment = "RIGHT"
            split.operator("pie.load_xz_keys_presets", text="手动执行")
        else:
            row.alignment = "LEFT"
            row.prop(self, "load_xz_keys_presets", text=text_hotkey)

        row = box.row()
        text_setting_presets = "加载预设 - 通用设置 (请备份好您的userpref.blend文件!)"
        if self.load_xz_setting_presets:
            split = row.column().split(factor=0.8)
            split.alignment = "LEFT"
            split.prop(self, "load_xz_setting_presets", text=text_setting_presets)
            split.alignment = "RIGHT"
            split.operator("pie.load_xz_setting_presets", text="手动执行")
        else:
            row.alignment = "LEFT"
            row.prop(self, "load_xz_setting_presets", text=text_setting_presets)

    def draw_other_addons_setting(self, layout):
        layout.label(text="其他插件设置")
        layout = self.layout.column(align=False)

        # 实用小工具设置
        attr, col = prefs_show_sub_panel(self, layout, "show_other_module_prop")
        if attr:
            box = col.box()
            col = box.column(align=True)
            row = col.row()
            row.prop(self, "modifier_profiling")
            row.prop(self, "change_overlay_and_shading_sets")

        # 表达式转节点
        attr, col = prefs_show_sub_panel(self, layout, "show_formula2nodes_submenu")
        if attr:
            box = col.box()
            box.label(text="检查键映射设置以编辑激活。默认为Ctrl+M")
            row = box.row(align=True)
            row.prop(self, "debug_prints")
            row.prop(self, "generate_previews")
            row = box.row()
            row.label(text="变量排序依据...")
            row.prop(self, "sort_vars", expand=True)

        # meshmachine剥离版
        attr, col = prefs_show_sub_panel(self, layout, "show_meshmachine_submenu")
        if attr:
            box = col.box()
            col = box.column(align=True)
            row = col.row()
            row.prop(self, "modal_hud_color")
            row.prop(self, "modal_hud_scale")
            row = col.row()
            row.prop(self, "modal_hud_hints")
            row.prop(self, "symmetrize_flick_distance")
        # 双语切换设置
        attr, col = prefs_show_sub_panel(self, layout, "show_language_switch_submenu")
        if attr:
            box = col.box()
            col = box.column(align=True)
            col.label(text="双语切换设置:设置不同的两种语言以供切换", icon="SETTINGS")
            row = col.row(align=True)
            row.prop(self, "first_lang")
            row.separator()
            row.prop(self, "second_lang")
        # 资产浏览器缩略图缩放快捷键
        attr, col = prefs_show_sub_panel(self, layout, "show_asset_browser_scroll")
        if attr:
            box = col.box()
            col = box.column(align=True)
            row = col.row()
            row.prop(self, "tby_bsr_multiplier_resize_factor")

        # 挤出流形插件
        attr, col = prefs_show_sub_panel(self, layout, "show_punchit")
        if attr:
            box = col.box()
            col = box.column(align=True)
            row = col.row()
            row.prop(self, "push_default")
            row.prop(self, "pull_default")
            row = col.row()
            row.prop(self, "non_manifold_extrude")
            row.prop(self, "modal_hud_timeout")


for mod in all_modules:
    # info = mod.bl_info
    mod_name = mod.__name__.split(".")[-1]

    def gen_update(mod):
        def update(self, context):
            enabled = getattr(self, "use_" + mod.__name__.split(".")[-1])
            if enabled:
                register_submodule(mod)
            else:
                unregister_submodule(mod)
            mod.__addon_enabled__ = enabled

        return update

    create_property(
        WXZ_PIE_Preferences,
        "use_" + mod_name,
        BoolProperty(
            # name=info["name"],
            name=mod_name,
            # name=mod.__name__.split(".")[0],
            # description=info.get("description", ""),
            update=gen_update(mod),
            default=True,
        ),
    )

classes = (
    PIE_UL_setting_modules,
    PIE_UL_pie_modules,
    PIE_UL_other_modules,
    WXZ_PIE_Preferences,
    PIE_OT_PIPInstall,
    PIE_OT_PIPInstall_Default,
    PIE_OT_PIPRemove,
    PIE_OT_ClearText,
    PIE_OT_PIPList,
    PIE_OT_EnsurePIP,
    PIE_OT_UpgradePIP,
)
class_register, class_unregister = bpy.utils.register_classes_factory(classes)


def add_modules_item(prefs, module_list_name):
    module = getattr(prefs, module_list_name)
    module.clear()
    for mod in all_modules_dir[module_list_name]:
        item = module.add()
        item.name = mod.__name__.split(".")[-1]


def register():
    class_register()
    props.register()
    global ERROR_OUTPUT
    global TEXT_OUTPUT

    prefs = get_addon_preferences()
    for mod in all_modules:
        if not hasattr(mod, "__addon_enabled__"):
            mod.__addon_enabled__ = False
        name = mod.__name__.split(".")[-1]
        if getattr(prefs, "use_" + name):
            register_submodule(mod)

    add_modules_item(prefs, "setting_modules")
    add_modules_item(prefs, "other_modules")
    add_modules_item(prefs, "pie_modules")

    try:
        bpy.app.translations.register(__package__, GetTranslationDict())
    except Exception as e:
        print(e)


def unregister():
    class_unregister()
    props.unregister()

    for mod in all_modules:
        if mod.__addon_enabled__:
            unregister_submodule(mod)
    try:
        bpy.app.translations.unregister(__package__)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    register()
