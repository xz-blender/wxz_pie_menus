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

from . import operators, props
from .panels import *
from .translation.translate import GetTranslationDict
from .utils import *

except_module_list = [
    "icons",
    "__pycache__",
    ".DS_Store",
    "utils",
    "Brush-key",
    "operator_id",
    "operator_id_sort",
    "extensions_setting",
    "assets_lib_presets",
    "addons_lib_presets",
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


class WXZ_PIE_Preferences(AddonPreferences, props.WXZ_PIE_Prefs_Props):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "tabs", expand=True)
        row.alignment = "CENTER"

        if self.tabs == "DEPENDENCIES":
            self.draw_dependencies(layout)
        elif self.tabs == "ADDON_MENUS":
            draw_addon_menus(self, layout, context, module_path_name_list)
        elif self.tabs == "RESOURCE_CONFIG":
            draw_resource_config(self, layout)
        elif self.tabs == "Other_Addons_Setting":
            draw_other_addons_setting(self, layout)

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
            name=mod_name,
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
    operators.register()
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
    operators.unregister()

    for mod in all_modules:
        if mod.__addon_enabled__:
            unregister_submodule(mod)
    try:
        bpy.app.translations.unregister(__package__)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    register()
