"""Load the host preferences and E module in a disposable Blender session."""
import importlib
from pathlib import Path
import sys

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


def register():
    addon.preferences.register()
    entry = bpy.context.preferences.addons.new()
    entry.module = addon.__name__
    addon.register_submodule(e_pie)


def unregister():
    operators.cancel_active()
    addon.unregister_submodule(e_pie)
    entry = bpy.context.preferences.addons.get(addon.__name__)
    if entry:
        bpy.context.preferences.addons.remove(entry)
    addon.preferences.unregister()
