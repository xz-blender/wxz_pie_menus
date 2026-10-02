"""Load the host preferences and E module in a disposable Blender session."""

import importlib
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
addon = importlib.import_module(ROOT.name)
e_pie = importlib.import_module(f"{ROOT.name}.pie.E_pie")
embedded = importlib.import_module(f"{ROOT.name}.module.quick_crease_weight")
operators = importlib.import_module(f"{embedded.__name__}.operators")
preferences = importlib.import_module(f"{embedded.__name__}.preferences")
hud = importlib.import_module(f"{embedded.__name__}.hud")
WeightEdit = importlib.import_module(f"{embedded.__name__}.mesh_data").WeightEdit
_lifecycle = addon.AddonLifecycle(
    {"pie_modules": [e_pie]},
    addon._lifecycle_host,
    before_features=(addon._core_step("preferences"),),
)


def register():
    entry = bpy.context.preferences.addons.new()
    entry.module = addon.__name__
    addon.bind_lifecycle(_lifecycle)
    _lifecycle.start()


def unregister():
    operators.cancel_active()
    _lifecycle.stop()
    addon.bind_lifecycle(addon._lifecycle)
    entry = bpy.context.preferences.addons.get(addon.__name__)
    if entry:
        bpy.context.preferences.addons.remove(entry)
