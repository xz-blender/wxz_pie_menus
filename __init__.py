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
from bpy.props import BoolProperty, PointerProperty
from bpy.types import AddonPreferences, Operator, PropertyGroup

from . import auto_load
from .nodes_presets.Higssas import *
from .pie.utils import change_default_keymap, check_rely_addon, rely_addons
from .translation.translate import GetTranslationDict
from .utils import *

# auto_load.init()

# from .prefrences import PIE_Preferences

bl_info = {
    "name": "WXZ Pie Menus Addon",
    "author": "wxz",
    "version": (0, 0, 8),
    "blender": (4, 0, 0),
    "description": "Pie Menu",
    "category": "3D View",
}
cwd = Path(__file__).parent
except_module_list = [
    "icons",
    "__pycache__",
    "utils",
    "Brush-key",
    "operator_id",
    "operator_id_sort",
    "extensions_setting",
]

module_list = [
    "pie",
    "operator",
    "parts_addons",
]
all_modules = []
for module in module_list:
    module_folder_path = Path(cwd) / module
    all_modules += iter_submodules_name(module_folder_path, except_module_list)


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


class WXZ_PIE_Preferences(AddonPreferences):
    bl_idname = get_addon_name()

    def draw(self, context):

        layout = self.layout
        box = layout.box()

        column = box.column()
        box = column.box()
        row = box.row()
        row.alignment = "CENTER"
        row.label(text="已启用以下Pie插件 :")

        for mod in all_modules:
            mod_name = mod.__name__.split(".")[-1]
            info = mod.bl_info
            box = column.box()
            row = box.row()
            sub = row.row()
            sub.context_pointer_set("addon_prefs", self)
            sub.label(
                icon="DOT",
                text="%s" % (info["name"]),
            )
            sub = row.row()
            sub.alignment = "RIGHT"
            sub.prop(self, "use_" + mod_name, text="")

        row = layout.box().row()
        row.alignment = "CENTER"
        row.label(text="End of Pie Menu Activations", icon="FILE_PARENT")


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
    WXZ_PIE_Preferences,
    Empty_Operator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    prefs = get_addon_preferences()

    for mod in all_modules:
        if not hasattr(mod, "__addon_enabled__"):
            mod.__addon_enabled__ = False
        name = mod.__name__.split(".")[-1]
        if getattr(prefs, "use_" + name):
            register_submodule(mod)

    try:
        bpy.app.translations.register(__package__, GetTranslationDict())
    except Exception as e:
        print(e)

    # auto_load.register()


def unregister():
    for mod in all_modules:
        if mod.__addon_enabled__:
            unregister_submodule(mod)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # auto_load.unregister()

    try:
        bpy.app.translations.unregister(__package__)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    register()
