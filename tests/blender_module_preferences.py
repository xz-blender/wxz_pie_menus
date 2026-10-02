"""Run with blender --background --factory-startup --python-exit-code 1 --python this_file.

Load the preferences package and root registration functions without enabling
unrelated operators, keymaps, or startup handlers of the add-on.
"""

import ast
import importlib
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

import bpy

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "wxz_module_preferences_test"
COLLECTIONS = ("pie_modules", "other_modules", "setting_modules")


def load_nodes(filename, select, namespace):
    tree = ast.parse((ROOT / filename).read_text(encoding="utf-8"))
    tree.body = [node for node in tree.body if select(node)]
    exec(compile(tree, str(ROOT / filename), "exec"), namespace)


package = ModuleType(PACKAGE)
package.__package__ = PACKAGE
package.__path__ = [str(ROOT)]
sys.modules[PACKAGE] = package
preferences = importlib.import_module(f"{PACKAGE}.prefs")
utils = importlib.import_module(f"{PACKAGE}.utils")
assert preferences.WXZ_PIE_Preferences.bl_idname == PACKAGE
addon = bpy.context.preferences.addons.new()
addon.module = PACKAGE
unused_module = SimpleNamespace(register=lambda: None, unregister=lambda: None)
modules_ns = dict(globals(), operators=unused_module, pip_operators=unused_module)
load_nodes(
    "__init__.py",
    lambda node: isinstance(node, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == "module_classes" for t in node.targets),
    modules_ns,
)
module_classes = modules_ns["module_classes"]
all_modules = []
all_modules_dir = {
    name: [SimpleNamespace(__name__="wxz.first"), SimpleNamespace(__name__="wxz.second")]
    for name in COLLECTIONS
}
translate = SimpleNamespace(register=lambda: None, unregister=lambda: None)


def get_addon_preferences():
    return addon.preferences


load_nodes(
    "__init__.py",
    lambda node: isinstance(node, ast.FunctionDef) and node.name in {"add_modules_item", "register", "unregister"},
    globals(),
)

for cycle in range(2):
    if cycle:
        previous_class = preferences.WXZ_PIE_Preferences
        importlib.reload(preferences)
        assert preferences.WXZ_PIE_Preferences is not previous_class
        assert preferences.WXZ_PIE_Preferences.bl_idname == PACKAGE
    register()
    try:
        prefs = get_addon_preferences()
        assert utils.get_prefs() == prefs
        assert prefs.use_china_mirror is True
        assert prefs.quick_crease_weight.sensitivity > 0
        assert hasattr(bpy.types.Scene, "M4_split")
        assert hasattr(bpy.types.Scene, "PIE_pip_output")
        assert all(cls.is_registered for cls in preferences.panels.CLASSES)
        for name in COLLECTIONS:
            collection = getattr(prefs, name)
            assert [item.name for item in collection] == ["first", "second"], name
            assert collection["first"].name == "first", name
            collection[0].name = "renamed"
            assert collection["renamed"].name == "renamed", name
            add_modules_item(prefs, name)
            assert [item.name for item in collection] == ["first", "second"], name
    finally:
        unregister()
    assert not preferences.WXZ_PIE_Preferences.is_registered
    for module in (preferences.props, preferences.pip_props, preferences.panels):
        assert all(not cls.is_registered for cls in module.CLASSES)
    assert not hasattr(bpy.types.Scene, "M4_split")
    assert not hasattr(bpy.types.Scene, "PIE_pip_output")
    print(f"PASS: preference imports, lookup, collections, registration and reload cycle {cycle + 1}")

bpy.context.preferences.addons.remove(addon)
