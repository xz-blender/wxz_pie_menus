"""Run with Blender --background --factory-startup --python-exit-code 1 --python this_file.

Check real RNA registration and Blender Python without installing or removing packages.
"""

import ast
import importlib
from pathlib import Path
import subprocess
import sys
from types import ModuleType
from unittest.mock import patch

import bpy
from bpy.props import *


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "wxz_pip_integration_test"
PIP_PREFS = {"debug"}


def load_nodes(filename, select, namespace):
    source = ast.parse((ROOT / filename).read_text(encoding="utf-8"))
    source.body = [node for node in source.body if select(node)]
    exec(compile(source, str(ROOT / filename), "exec"), namespace)


package = ModuleType(PACKAGE)
package.__path__ = [str(ROOT)]
sys.modules[PACKAGE] = package
utils = ModuleType(f"{PACKAGE}.utils")
utils.bpy = bpy
load_nodes(
    "utils.py",
    lambda node: isinstance(node, ast.FunctionDef) and node.name in {"safe_register_class", "safe_unregister_class"},
    vars(utils),
)
sys.modules[utils.__name__] = utils

pip_props = importlib.import_module(f"{PACKAGE}.module.pip_helper.props")
scope = dict(globals())
source = ast.parse((ROOT / "props.py").read_text(encoding="utf-8"))
mixin = next(node for node in source.body if isinstance(node, ast.ClassDef) and node.name == "WXZ_PIE_Prefs_Props")
mixin.body = [node for node in mixin.body if isinstance(node, ast.AnnAssign) and node.target.id in PIP_PREFS]
exec(compile(ast.Module(body=[mixin], type_ignores=[]), str(ROOT / "props.py"), "exec"), scope)


class ProbePreferences(bpy.types.AddonPreferences, scope["WXZ_PIE_Prefs_Props"], pip_props.PIP_Prefs_Props):
    bl_idname = PACKAGE


utils.get_prefs = lambda: bpy.context.preferences.addons[PACKAGE].preferences
ops = importlib.import_module(f"{PACKAGE}.module.pip_helper.operators")
commands = importlib.import_module(f"{PACKAGE}.module.pip_helper.commands")
python = Path(commands.python_bin)
assert python.is_file(), python
assert python.stem.startswith("python"), python
print(f"PASS: Blender {bpy.app.version_string} Python resolved to {python}")

for cycle in range(2):
    pip_props.register()
    utils.safe_register_class([ProbePreferences])
    entry = bpy.context.preferences.addons.new()
    entry.module = PACKAGE
    ops.register()
    try:
        prefs = entry.preferences
        assert prefs.use_china_mirror is True
        assert prefs.install_custom_pip_packages == ""
        prefs.install_custom_pip_packages = "  pillow   requests "
        assert all(cls.is_registered for cls in ops.CLASSES)
        with patch.object(commands.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "ok", "warning")) as run:
            assert bpy.ops.pie.pip_install() == {"FINISHED"}
            assert "pillow" in run.call_args.args[0]
            assert "-i" in run.call_args.args[0]
            assert bpy.ops.pie.pip_remove() == {"FINISHED"}
            assert run.call_args.args[0][3:] == ["uninstall", "pillow", "requests", "-y"]
            assert bpy.ops.pie.pip_install_default() == {"FINISHED"}
            assert set(ops.PIP_Packeges_Dict).issubset(run.call_args.args[0])
            assert bpy.ops.pie.ensure_pip() == {"FINISHED"}
            assert bpy.ops.pie.upgrade_pip() == {"FINISHED"}
        # A real, read-only subprocess checks that the resolved interpreter runs pip.
        assert bpy.ops.pie.pip_show_list() == {"FINISHED"}
        assert bpy.context.scene.PIE_pip_output.RETRUNCODE_OUTPUT == "成功"
        assert len(bpy.context.scene.PIE_pip_output.TEXT_OUTPUT) > 0
        assert bpy.ops.pie.pip_cleartext() == {"FINISHED"}
        assert not bpy.context.scene.PIE_pip_output.TEXT_OUTPUT
        print(f"PASS: pip preferences, operators, output and registration cycle {cycle + 1}")
    finally:
        ops.unregister()
        bpy.context.preferences.addons.remove(entry)
        utils.safe_unregister_class([ProbePreferences])
        pip_props.unregister()
    assert all(not cls.is_registered for cls in ops.CLASSES)
    assert all(not cls.is_registered for cls in pip_props.CLASSES)
    assert not hasattr(bpy.types.Scene, "PIE_pip_output")

print(f"Native multiline labels: {hasattr(bpy.types.UILayout, 'label_multiline')}")
