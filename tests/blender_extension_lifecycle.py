"""Exercise real extension-namespace lifecycle with populated preferences offline."""
import shutil
import sys
import tempfile
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="wxz-extension-cycle-") as directory:
    repo_dir = Path(directory)
    target = repo_dir / "wxz_pie_menus"
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(
        ".git", ".venv", "dist", "__pycache__", ".ruff_cache", "*.pyc",
    ))
    bpy.ops.preferences.extension_repo_add(
        name="WXZ Lifecycle Test", type="LOCAL", use_custom_directory=True, custom_directory=str(repo_dir),
    )
    repo = next(repo for repo in bpy.context.preferences.extensions.repos if repo.directory == str(repo_dir))
    module_name = f"bl_ext.{repo.module}.wxz_pie_menus"
    for cycle in range(10):
        assert bpy.ops.preferences.addon_enable(module=module_name) == {"FINISHED"}
        addon = sys.modules[module_name]
        try:
            prefs = bpy.context.preferences.addons[module_name].preferences
            for tab in ("DEPENDENCIES", "ADDON_MENUS", "RESOURCE_CONFIG", "Other_Addons_Setting"):
                prefs.tabs = tab
            prefs.show_quick_crease_weight = True
            assert prefs.quick_crease_weight.sensitivity > 0
            prefs.use_A_pie = False
            prefs.use_A_pie = True
            states = [addon._lifecycle.status(mod.__name__.rsplit(".", 1)[-1]) for mod in addon.all_modules]
            assert all(not state.errors and state.state.value == "active" for state in states), states
        finally:
            assert bpy.ops.preferences.addon_disable(module=module_name) == {"FINISHED"}
        assert all(addon._lifecycle.status(mod.__name__.rsplit(".", 1)[-1]).state.value == "disabled"
                   for mod in addon.all_modules)
        print(f"PASS: extension namespace, preferences, feature toggle, full lifecycle {cycle + 1}/10", flush=True)
