"""Check preference package registration and reload through the root lifecycle.

Run with blender --background --factory-startup --python-exit-code 1 --python this_file.
"""

import ast
import importlib
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import bpy

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "wxz_preferences_package_test"
package = ModuleType(PACKAGE)
package.__package__ = PACKAGE
package.__path__ = [str(ROOT)]
sys.modules[PACKAGE] = package
preferences = importlib.import_module(f"{PACKAGE}.prefs")
utils = importlib.import_module(f"{PACKAGE}.utils")
core = importlib.import_module(f"{PACKAGE}.module.lifecycle")
adapter = importlib.import_module(f"{PACKAGE}.module.lifecycle_blender")

groups = {
    name: [SimpleNamespace(__name__=f"wxz.{feature}", register=lambda: None, unregister=lambda: None)]
    for name, feature in zip(preferences.MODULE_PATH_NAMES.values(), ("first", "second", "third"))
}
unused_module = SimpleNamespace(register=lambda: None, unregister=lambda: None)
scope = {
    "__package__": PACKAGE,
    "preferences": preferences,
    "operators": unused_module,
    "pip_operators": unused_module,
    "translate": unused_module,
    "all_modules_dir": groups,
    "AddonLifecycle": core.AddonLifecycle,
    "LifecycleStep": core.LifecycleStep,
    "BlenderLifecycleHost": adapter.BlenderLifecycleHost,
}
tree = ast.parse((ROOT / "__init__.py").read_text(encoding="utf-8"))
tree.body = [
    node
    for node in tree.body
    if (isinstance(node, ast.FunctionDef) and node.name in {"_core_step", "register", "unregister"})
    or (
        isinstance(node, ast.If)
        and isinstance(node.test, ast.Compare)
        and isinstance(node.test.left, ast.Constant)
        and node.test.left.value == "_lifecycle"
    )
]
addon = bpy.context.preferences.addons.new()
addon.module = PACKAGE
try:
    for cycle in range(2):
        if cycle:
            previous_class = preferences.WXZ_PIE_Preferences
            importlib.reload(preferences)
            assert preferences.WXZ_PIE_Preferences is not previous_class
        assert preferences.WXZ_PIE_Preferences.bl_idname == PACKAGE
        adapter.bind_module_toggles(
            preferences.WXZ_PIE_Preferences, [mod for modules in groups.values() for mod in modules]
        )
        scope["WXZ_PIE_Preferences"] = preferences.WXZ_PIE_Preferences
        exec(compile(tree, str(ROOT / "__init__.py"), "exec"), scope)  # noqa: S102
        adapter.bind_lifecycle(scope["_lifecycle"])
        scope["register"]()
        try:
            prefs = addon.preferences
            assert utils.get_prefs() == prefs
            assert prefs.use_china_mirror is True
            assert prefs.quick_crease_weight.sensitivity > 0
            assert hasattr(bpy.types.Scene, "M4_split")
            assert hasattr(bpy.types.Scene, "PIE_pip_output")
            assert all(cls.is_registered for cls in preferences.panels.CLASSES)
            for name, modules in groups.items():
                expected = [mod.__name__.rsplit(".", 1)[-1] for mod in modules]
                collection = getattr(prefs, name)
                assert [item.name for item in collection] == expected
                assert collection[expected[0]].name == expected[0]
                collection[0].name = "renamed"
                assert collection["renamed"].name == "renamed"
                scope["_lifecycle_host"].rebuild_collections(groups)
                assert [item.name for item in collection] == expected
        finally:
            scope["unregister"]()
        assert not preferences.WXZ_PIE_Preferences.is_registered
        for module in (preferences.props, preferences.pip_props, preferences.panels):
            assert all(not cls.is_registered for cls in module.CLASSES)
        assert not hasattr(bpy.types.Scene, "M4_split")
        assert not hasattr(bpy.types.Scene, "PIE_pip_output")
        print(f"PASS: preference package, root lifecycle, collections and reload cycle {cycle + 1}")
finally:
    adapter.bind_lifecycle(None)
    bpy.context.preferences.addons.remove(addon)
