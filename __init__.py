import inspect
from pathlib import Path

from . import prefs as preferences
from .module.lifecycle import AddonLifecycle, LifecycleStep
from .module.lifecycle_blender import BlenderLifecycleHost, bind_lifecycle, bind_module_toggles

if "bpy" in locals():
    import importlib

    for core_name in ("preferences", "operators", "pip_operators"):
        importlib.reload(globals()[core_name])
else:
    import bpy
    from bpy.props import PointerProperty
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
        if inspect.isclass(obj) and issubclass(obj, PropertyGroup) and getattr(obj, "bl_idname", None) == mod.__name__:
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
        cls.__annotations__ = {}
    cls.__annotations__[name] = prop


bind_module_toggles(WXZ_PIE_Preferences, all_modules)

module_classes = [
    operators,
    pip_operators,
]
addon_keymaps = []


def _core_step(name):
    # Resolve reloaded core modules when the hook runs, not at composition time.
    return LifecycleStep(name, lambda: globals()[name].register(), lambda: globals()[name].unregister())


if "_lifecycle" not in locals():
    _lifecycle_host = BlenderLifecycleHost(__package__, lambda: WXZ_PIE_Preferences)
    _lifecycle = AddonLifecycle(
        all_modules_dir,
        _lifecycle_host,
        before_features=(
            _core_step("preferences"),
            _core_step("operators"),
            _core_step("pip_operators"),
        ),
        after_features=(
            LifecycleStep(
                "module_lists",
                lambda: _lifecycle_host.rebuild_collections(_lifecycle.groups),
                lambda: None,
            ),
            _core_step("translate"),
        ),
    )
bind_lifecycle(_lifecycle)


def register():
    _lifecycle.start()


def unregister():
    _lifecycle.stop()
