import inspect
from pathlib import Path

from . import prefs as preferences

if "bpy" in locals():
    import importlib

    importlib.reload(preferences)
    importlib.reload(operators)
    importlib.reload(pip_operators)
else:
    import bpy
    from bpy.props import BoolProperty, PointerProperty
    from bpy.types import PropertyGroup

    from . import operators
    from .module.pip_helper import operators as pip_operators
    from .translation import translate
    from .utils import iter_submodules_name

from .prefs import WXZ_PIE_Preferences

except_module_list = [
    "icons",
    "__pycache__",
    ".DS_Store",
    "utils",
    "pie_utils",
    "Brush_key",
    "operator_id_sort",
    "extensions_setting",
]
cwd = Path(__file__).parent
module_path_name_list = preferences.MODULE_PATH_NAMES
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
    operators,
    pip_operators,
]
addon_keymaps = []


def add_modules_item(prefs, module_list_name):
    module = getattr(prefs, module_list_name)
    module.clear()
    for mod in all_modules_dir[module_list_name]:
        item = module.add()
        item.name = mod.__name__.split(".")[-1]


def register():
    preferences.register()
    for mod in module_classes:
        mod.register()

    prefs = get_addon_preferences()
    for mod in all_modules:
        if not hasattr(mod, "__addon_enabled__"):
            mod.__addon_enabled__ = False
        name = mod.__name__.split(".")[-1]
        if prefs is None or getattr(prefs, "use_" + name):
            register_submodule(mod)

    if prefs is not None:
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

    preferences.unregister()
    translate.unregister()
