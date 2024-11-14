from pathlib import Path

from .download import download_file, download_zip
from .packup import packup_split_file_list, packup_split_folder_list

down_path = Path(__file__).parent
xz_url = "addons_file/" + str(down_path.name) + "/"
try:
    for file in packup_split_file_list:
        download_file(xz_url + file, down_path)
    for dir in packup_split_folder_list:
        download_zip(xz_url + dir + ".zip", down_path)
except Exception:
    print(file, "子插件下载失败,请检查网络!")


import inspect

if "bpy" in locals():
    import importlib

    importlib.reload(props)
    importlib.reload(operators)
    importlib.reload(panels)
    importlib.reload(pip_package)
else:
    import bpy
    from bpy.props import *
    from bpy.types import AddonPreferences, Operator, PropertyGroup

    from . import operators, panels, pip_package, props
    from .translation import translate
    from .utils import *

except_module_list = [
    "icons",
    "__pycache__",
    ".DS_Store",
    "utils",
    "pie_utils",
    "Brush-key",
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


def _get_pref_class(mod):
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


class WXZ_PIE_Preferences(AddonPreferences, props.WXZ_PIE_Prefs_Props):
    bl_idname = __package__

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "tabs", expand=True)
        row.alignment = "CENTER"

        if self.tabs == "DEPENDENCIES":
            panels.draw_dependencies(self, layout)
        elif self.tabs == "ADDON_MENUS":
            panels.draw_addon_menus(self, layout, context, module_path_name_list)
        elif self.tabs == "RESOURCE_CONFIG":
            panels.draw_resource_config(self, layout)
        elif self.tabs == "Other_Addons_Setting":
            panels.draw_other_addons_setting(self, layout)


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

module_classes = [
    props,
    operators,
    pip_package,
    panels,
]
addon_keymaps = []


def add_modules_item(prefs, module_list_name):
    module = getattr(prefs, module_list_name)
    module.clear()
    for mod in all_modules_dir[module_list_name]:
        item = module.add()
        item.name = mod.__name__.split(".")[-1]


def register():
    bpy.utils.register_class(WXZ_PIE_Preferences)
    for mod in module_classes:
        mod.register()

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

    translate.register()


def unregister():

    for mod in reversed(module_classes):
        mod.unregister()

    for mod in all_modules:
        if mod.__addon_enabled__:
            unregister_submodule(mod)

    bpy.utils.unregister_class(WXZ_PIE_Preferences)
    translate.unregister()
