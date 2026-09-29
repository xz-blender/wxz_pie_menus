"""Run with blender --background --factory-startup --python-exit-code 1 --python this_file.

Exercise real module discovery and registration with the removed bgl module
explicitly unavailable, including on Blender versions that still provide it.
"""

import builtins
import importlib
import sys
from pathlib import Path
from unittest.mock import patch

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
original_import = builtins.__import__


def import_without_bgl(name, *args, **kwargs):
    if name == "bgl" or name.startswith("bgl."):
        raise ModuleNotFoundError("No module named 'bgl'", name="bgl")
    return original_import(name, *args, **kwargs)


with patch("builtins.__import__", side_effect=import_without_bgl):
    addon = importlib.import_module(ROOT.name)
    assert Path(addon.__file__).resolve() == ROOT / "__init__.py"
    preferences_entry = bpy.context.preferences.addons.new()
    preferences_entry.module = addon.__name__
    saved_off_name = addon.all_modules_dir["pie_modules"][0].__name__.rsplit(".", 1)[-1]
    try:
        for cycle in range(2):
            addon.register()
            try:
                assert addon.WXZ_PIE_Preferences.is_registered
                prefs = preferences_entry.preferences
                assert prefs.use_china_mirror is True
                assert prefs.install_custom_pip_packages == ""
                assert hasattr(bpy.types.Scene, "PIE_pip_output")
                if cycle:
                    assert getattr(prefs, "use_" + saved_off_name) is False
                    assert addon._lifecycle.status(saved_off_name).state.value == "disabled"
                for collection_name, modules in addon.all_modules_dir.items():
                    assert [item.name for item in getattr(prefs, collection_name)] == [
                        module.__name__.split(".")[-1] for module in modules
                    ], collection_name
                setattr(prefs, "use_" + saved_off_name, False)
                assert addon._lifecycle.status(saved_off_name).desired is False
            finally:
                addon.unregister()
            assert not addon.WXZ_PIE_Preferences.is_registered
            assert not hasattr(bpy.types.Scene, "PIE_pip_output")
            print(f"PASS: full startup, preferences, and shutdown without bgl, cycle {cycle + 1}")
    finally:
        bpy.context.preferences.addons.remove(preferences_entry)
