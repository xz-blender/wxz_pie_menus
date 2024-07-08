import inspect
import os
from pathlib import Path

from .download import download_file, download_zip

down_path = Path(__file__).parent
xz_url = "addons_file" + "/" + down_path.name + "/"

down_path = Path(__file__).parent
download_file("fonts/ui_font.ttf", down_path)
download_file(xz_url + "workspace.blend", down_path)
download_file(xz_url + "workspace_online.blend", down_path)

import bpy
from bpy.props import BoolProperty, CollectionProperty, IntProperty, PointerProperty, StringProperty
from bpy.types import AddonPreferences, Operator, PropertyGroup, UIList

from .nodes_presets.Higssas import *
from .translation.translate import GetTranslationDict
from .utils import *

bl_info = {
    "name": "WXZ Pie Menus Addon",
    "author": "wxz",
    "version": (0, 0, 8),
    "blender": (4, 0, 0),
    "description": "Pie Menu",
    "category": "3D View",
}

except_module_list = [
    "icons",
    "__pycache__",
    "utils",
    "Brush-key",
    "operator_id",
    "operator_id_sort",
    "extensions_setting",
]

cwd = Path(__file__).parent
pie_modules = iter_submodules_name(Path(cwd) / "pie", except_module_list)
other_modules = iter_submodules_name(Path(cwd) / "parts_addons", except_module_list)
setting_modules = iter_submodules_name(Path(cwd) / "operator", except_module_list)
all_modules = pie_modules + other_modules + setting_modules
all_modules_dir = {"pie_modules": pie_modules, "other_modules": other_modules, "setting_modules": setting_modules}


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


class Empty_Operator(Operator):
    bl_idname = "pie.empty_operator"
    bl_label = ""

    def execute(self, context):
        return {"CANCELLED"}


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


class WXZ_PIE_Preferences(AddonPreferences):
    bl_idname = get_addon_name()

    package_pyclipper: bpy.props.BoolProperty(name="PyClipper Installed", default=False)  # type: ignore
    tabs: bpy.props.EnumProperty(
        items=(
            ("DEPENDENCIES", "依赖包", ""),
            ("ADDON_MENUS", "饼菜单", ""),
            ("RESOURCE_CONFIG", "资源配置", ""),
        ),
        default="ADDON_MENUS",
    )  # type: ignore
    pie_modules: CollectionProperty(type=PropertyGroup)  # type: ignore
    pie_modules_index: bpy.props.IntProperty()  # type: ignore
    other_modules: CollectionProperty(type=PropertyGroup)  # type: ignore
    other_modules_index: bpy.props.IntProperty()  # type: ignore
    setting_modules: CollectionProperty(type=PropertyGroup)  # type: ignore
    setting_modules_index: bpy.props.IntProperty()  # type: ignore

    package_pyclipper: bpy.props.BoolProperty(name="PyClipper Installed", default=False)  # type: ignore
    package_pillow: bpy.props.BoolProperty(name="Pillow Installed", default=False)  # type: ignore
    package_openai: bpy.props.BoolProperty(name="OpenAI Installed", default=False)  # type: ignore
    package_httpx: bpy.props.BoolProperty(name="HTTPX Installed", default=False)  # type: ignore
    package_requests: bpy.props.BoolProperty(name="Requests Installed", default=False)  # type: ignore

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

    def draw_dependencies(self, layout):
        layout.label(text="依赖包设置")
        box1 = layout.box()
        row = box1.row()
        row.label(text="依赖关系管理")
        row.separator()
        row.operator("pie.check_dependencies", text="刷新", icon="FILE_REFRESH")

        table_key = ["Package", "Status", "Actions", ""]
        packages = [
            {
                "name": "PyClipper",
                "signal": self.package_pyclipper,
                "operator1": "pie.dependencies_install",
                "operator2": "pie.dependencies_remove",
            },
            {
                "name": "Pillow",
                "signal": self.package_pillow,
                "operator1": "pie.dependencies_install",
                "operator2": "pie.dependencies_remove",
            },
            {
                "name": "OpenAI",
                "signal": self.package_openai,
                "operator1": "pie.dependencies_install",
                "operator2": "pie.dependencies_remove",
            },
            {
                "name": "HTTPX",
                "signal": self.package_httpx,
                "operator1": "pie.dependencies_install",
                "operator2": "pie.dependencies_remove",
            },
            {
                "name": "Requests",
                "signal": self.package_requests,
                "operator1": "pie.dependencies_install",
                "operator2": "pie.dependencies_remove",
            },
        ]
        column = box1.column()
        row = column.row()
        for key in table_key:
            row.label(text=key)
        for p in packages:
            row = column.row()
            row.label(text=p["name"])

            if p["signal"]:
                row.label(text="已安装")
            else:
                row.label(text="未安装")
            row.operator(p["operator1"])
            row.operator(p["operator2"])

    def draw_addon_menus(self, layout, context):
        layout.label(text="内置饼菜单 & 内置插件开关")
        top_row = layout.row()

        split = top_row.split()
        box = split.box()
        sub_row = box.row()
        sub_row.alignment = "CENTER"
        sub_row.label(text="已启用饼菜单:")
        sub_row = box.row()
        column = sub_row.column()
        column.template_list("PIE_UL_pie_modules", "", self, "pie_modules", self, "pie_modules_index", rows=8)

        split = top_row.split()
        box = split.box()
        sub_row = box.row()
        sub_row.alignment = "CENTER"
        sub_row.label(text="已启用内置插件:")
        sub_row = box.row()
        column = sub_row.column()
        column.template_list("PIE_UL_other_modules", "", self, "other_modules", self, "other_modules_index", rows=8)

        split = top_row.split()
        box = split.box()
        sub_row = box.row()
        sub_row.alignment = "CENTER"
        sub_row.label(text="已应用设置:")
        sub_row = box.row()
        column = sub_row.column()
        column.template_list(
            "PIE_UL_setting_modules", "", self, "setting_modules", self, "setting_modules_index", rows=8
        )

    def draw_resource_config(self, layout):
        layout.label(text="资源配置设置")


for mod in all_modules:
    info = mod.bl_info
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
            name=info["name"],
            # name=mod.__name__.split(".")[0],
            # description=info.get("description", ""),
            update=gen_update(mod),
            default=True,
        ),
    )

classes = (
    Empty_Operator,
    PIE_UL_setting_modules,
    PIE_UL_pie_modules,
    PIE_UL_other_modules,
    WXZ_PIE_Preferences,
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

    for mod in all_modules:
        if mod.__addon_enabled__:
            unregister_submodule(mod)
    try:
        bpy.app.translations.unregister(__package__)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    register()
