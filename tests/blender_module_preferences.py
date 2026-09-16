"""Run with blender --background --factory-startup --python-exit-code 1 --python this_file.

Load the real RNA declarations and registration functions without importing the
unrelated operators, dependencies, keymaps, or startup handlers of the add-on.
"""

import ast
from pathlib import Path
from types import SimpleNamespace

import bpy
from bpy.props import *
from bpy.types import AddonPreferences, PropertyGroup

ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS = ("pie_modules", "other_modules", "setting_modules")


def load_nodes(filename, select, namespace):
    tree = ast.parse((ROOT / filename).read_text(encoding="utf-8"))
    tree.body = [node for node in tree.body if select(node)]
    exec(compile(tree, str(ROOT / filename), "exec"), namespace)


load_nodes(
    "utils.py",
    lambda node: isinstance(node, ast.FunctionDef)
    and node.name in {"safe_register_class", "safe_unregister_class"},
    globals(),
)

props_ns = dict(globals())
load_nodes(
    "props.py",
    lambda node: (isinstance(node, ast.ClassDef) and node.name != "WXZ_PIE_Prefs_Props")
    or (isinstance(node, ast.FunctionDef) and node.name in {"register", "unregister"})
    or (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CLASSES" for t in node.targets)),
    props_ns,
)
prefs_tree = ast.parse((ROOT / "props.py").read_text(encoding="utf-8"))
prefs_class = next(node for node in prefs_tree.body if isinstance(node, ast.ClassDef) and node.name == "WXZ_PIE_Prefs_Props")
prefs_class.body = [
    node for node in prefs_class.body
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id in COLLECTIONS
]
exec(compile(ast.Module(body=[prefs_class], type_ignores=[]), str(ROOT / "props.py"), "exec"), props_ns)
props = SimpleNamespace(**props_ns)


class WXZ_PIE_Preferences(AddonPreferences, props.WXZ_PIE_Prefs_Props):
    bl_idname = "wxz_module_preferences_test"


addon = bpy.context.preferences.addons.new()
addon.module = WXZ_PIE_Preferences.bl_idname
unused_module = SimpleNamespace(register=lambda: None, unregister=lambda: None)
pip_props = unused_module
modules_ns = dict(globals(), operators=unused_module, pip_operators=unused_module, panels=unused_module)
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
    register()
    prefs = get_addon_preferences()
    for name in COLLECTIONS:
        collection = getattr(prefs, name)
        assert [item.name for item in collection] == ["first", "second"], name
        assert collection["first"].name == "first", name
        collection[0].name = "renamed"
        assert collection["renamed"].name == "renamed", name
        add_modules_item(prefs, name)
        assert [item.name for item in collection] == ["first", "second"], name
    unregister()
    assert not WXZ_PIE_Preferences.is_registered
    assert all(not cls.is_registered for cls in props.CLASSES)
    print(f"PASS: module names, lookup, rebuild, and registration cycle {cycle + 1}")

bpy.context.preferences.addons.remove(addon)
